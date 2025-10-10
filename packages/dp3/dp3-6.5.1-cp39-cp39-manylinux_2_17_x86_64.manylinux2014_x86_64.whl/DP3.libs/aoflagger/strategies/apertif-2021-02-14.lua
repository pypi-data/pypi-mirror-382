--[[
 This is the Apertif Lua strategy, version 2021-02-14
 Author: André Offringa
 Compared to the standard AOFlagger strategy, it has roughly the following changes:
 - Take input flags into account (e.g. when the correlator produces missing data)
 - Any 'exact' zero visibility is flagged, as these are produced in case of correlator failure
 - Apply a bandpass file. The bandpass can be set with the "-preamble bandpass_filename='..'" parameter
 - Auto-correlations are flagged, and flagged with a different (less sensitive) strategy
 - Channels in the range 1418-1424 MHz are excluded from detection, as they are mostly without RFI and
   might contain strong HI in case a nearby Galaxy is observed. [Currently turned off]
 - Apart from that, settings like the thresholds and the smoothing filter strength have been tweaked to
   work well for Apertif.
]]

aoflagger.require_min_version("3.0.4")

-- Main flagging function that is called for every baseline. The input parameter represents the data for
-- a single baseline. Any changes to the flagging of 'input' are written back to the measurement set.
function execute(input)
  --
  -- Generic settings
  --

  -- What polarizations to flag? Default: input:get_polarizations() (=all that are in the input data)
  -- Other options are e.g.:
  -- { 'XY', 'YX' } to flag only XY and YX, or
  -- { 'I', 'Q' } to flag only on Stokes I and Q
  local flag_polarizations = input:get_polarizations()

  local base_threshold = 1.2 -- lower means more sensitive detection
  local iteration_count = 3 -- slowly increase sensitivity: how many iterations to do this?
  local threshold_factor_step = 2.0 -- How much to increase the sensitivity each iteration?
  local frequency_resize_factor = 175 -- Amount of "extra" smoothing in frequency direction
  local transient_threshold_factor = 1 -- decreasing this value puts more emphasis on detection of transient RFI
  -- How to flag complex values, options are: phase, amplitude, real, imaginary, complex
  local flag_representations = { "amplitude" }

  --
  -- End of generic settings
  --

  -- Some variables that we need later on:
  local isAutocorrelation = input:is_auto_correlation()
  local inpPolarizations = input:get_polarizations()

  if isAutocorrelation then
    base_threshold = 8 -- Because of the high S/N of autos, less sensitive detection is required
    iteration_count = 5 -- Auto-correlations have more dynamic range, so converge slightly slower
    frequency_resize_factor = 50 -- Auto-correlations have more structure in frequency direction, so smooth less
    transient_threshold_factor = 0.25 -- More emphasis on transients (~less emphasis on frequency structure)
    -- XY=YX for amplitude of autos, so there's no need to flag both
    for i, v in ipairs(flag_polarizations) do
      if v == "YX" then
        table.remove(flag_polarizations, i)
        break
      end
    end
  end

  if bandpass_filename ~= nil then
    aoflagger.apply_bandpass(input, bandpass_filename)
  end

  -- Any visibilities that are exactly zero? Flag them.
  for _, polarization in ipairs(input:get_polarizations()) do
    data = input:convert_to_polarization(polarization)
    data:flag_zeros()
    input:set_polarization_data(polarization, data)
  end

  local copy_of_input = input:copy()

  for ipol, polarization in ipairs(flag_polarizations) do
    data = input:convert_to_polarization(polarization)

    local original_data
    for _, representation in ipairs(flag_representations) do
      data = data:convert_to_complex(representation)
      original_data = data:copy()

      for i = 1, iteration_count - 1 do
        local threshold_factor = threshold_factor_step ^ (iteration_count - i)

        local sumthr_level = threshold_factor * base_threshold
        aoflagger.sumthreshold_masked(
          data,
          original_data,
          sumthr_level,
          sumthr_level * transient_threshold_factor,
          true,
          true
        )

        -- Do timestep & channel flagging
        if not isAutocorrelation then
          local chdata = data:copy()
          aoflagger.threshold_timestep_rms(data, 3.5)
          aoflagger.threshold_channel_rms(chdata, 3.0 * threshold_factor, true)
          data:join_mask(chdata)
        end

        -- High pass filtering steps
        data:set_visibilities(original_data)
        data:join_mask(original_data)
        local resized_data = aoflagger.downsample(data, 1, frequency_resize_factor, true)
        aoflagger.low_pass_filter(resized_data, 21, 31, 2.5, 5.0)
        aoflagger.upsample(resized_data, data, 1, frequency_resize_factor)

        -- In case this script is run from inside rfigui, calling
        -- the following visualize function will add the current result
        -- to the list of displayable visualizations.
        -- If the script is not running inside rfigui, the call is ignored.
        aoflagger.visualize(data, "Fit #" .. i, i - 1)

        local tmp = original_data - data
        tmp:set_mask(data)
        data = tmp

        aoflagger.visualize(data, "Residual #" .. i, i + iteration_count)
        aoflagger.set_progress((ipol - 1) * iteration_count + i, #inpPolarizations * iteration_count)
      end -- end of iterations

      aoflagger.sumthreshold_masked(
        data,
        original_data,
        base_threshold,
        base_threshold * transient_threshold_factor,
        true,
        true
      )
    end -- end of complex representation iteration

    data:join_mask(original_data)

    if not isAutocorrelation then
      aoflagger.threshold_timestep_rms(data, 4.0)
    end

    -- Helper function used in the strategy
    function contains(arr, val)
      for _, v in ipairs(arr) do
        if v == val then
          return true
        end
      end
      return false
    end

    if contains(inpPolarizations, polarization) then
      if input:is_complex() then
        data = data:convert_to_complex("complex")
      end
      input:set_polarization_data(polarization, data)
    else
      input:join_mask(polarization, data)
    end
    input:set_polarization_data(polarization, data)

    aoflagger.visualize(data, "Residual #" .. iteration_count, 2 * iteration_count)
    aoflagger.set_progress(ipol, #flag_polarizations)
  end -- end of polarization iterations

  aoflagger.scale_invariant_rank_operator_masked(input, copy_of_input, 0.2, 0.2)

  -- The following statement restores the flagging as it was before RFI detection
  -- for the frequency range 1418-1424 MHz. This range is considered clean for Apertif,
  -- hence any flags there are more likely to be false positives. This is in
  -- particular important when observing bright Galaxies that might show HI lines that
  -- are bright enough to get flagged.
  -- Turned off after testing 2020-05-19: broadband RFI causes the images to have striping
  -- input:set_mask_for_channel_range(copy_of_input, 1418, 1424)

  -- This command will calculate a few statistics like flag% and stddev over
  -- time, frequency and baseline and write those to the MS. These can be
  -- visualized with aoqplot.
  if input:has_metadata() then
    aoflagger.collect_statistics(input, copy_of_input)
  end
end

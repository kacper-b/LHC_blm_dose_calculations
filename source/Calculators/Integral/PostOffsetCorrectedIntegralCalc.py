import numpy as np

from source.BLM_dose_calculation_exceptions import IntegrationResultBelowZero, IntensityIntervalNotCoveredByBLMData, \
    NoBLMDataForIntensityInterval
from source.Calculators.Integral.IntegralCalc import IntegralCalc


class PostOffsetCorrectedIntegralCalc(IntegralCalc):
    def run(self, data, blm_intervals):
        col_name = data.columns[0]
        for blm_interval in blm_intervals:
            blm_beam_on_data = blm_interval.get_integrated_data(data) - blm_interval.offset_post
            try:
                integral_offset_corrected = self.__integrate(blm_beam_on_data, col_name, blm_interval)
            except (
                    IntegrationResultBelowZero, IntensityIntervalNotCoveredByBLMData,
                    NoBLMDataForIntensityInterval) as e:
                integral_offset_corrected = 0
            finally:
                blm_interval.integral_post_offset_corrected = integral_offset_corrected

    def __integrate(self, data, col_name, blm_interval):
        if not data.empty:
            integral = np.trapz(y=data[data.columns[0]], x=data.index)
            if integral < 0:
                raise IntegrationResultBelowZero('{} integrated dose < 0: {}'.format(col_name, blm_interval))
            return integral
        else:
            raise NoBLMDataForIntensityInterval(
                '{} dataframe for given intensity interval is empty: {}'.format(col_name, blm_interval))

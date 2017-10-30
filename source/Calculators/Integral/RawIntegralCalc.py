import numpy as np

from source.BLM_dose_calculation_exceptions import IntegrationResultBelowZero, IntensityIntervalNotCoveredByBLMData, \
    NoBLMDataForIntensityInterval
from source.Calculators.Integral.IntegralCalc import IntegralCalc


class RawIntegralCalc(IntegralCalc):
    def run(self, data, blm_intervals):
        col_name = data.columns[0]
        for blm_interval in blm_intervals:
            blm_beam_on_data = blm_interval.get_integrated_data(data)
            try:
                blm_interval.integral_raw = self.__integrate(blm_beam_on_data, col_name, blm_interval)
            except (
                    IntegrationResultBelowZero, IntensityIntervalNotCoveredByBLMData,
                    NoBLMDataForIntensityInterval) as e:
                blm_interval.integral_raw = 0
                e.logging_func('{}'.format(str(e)))

    def __integrate(self, data, col_name, blm_interval):
        if not data.empty:
            integral = np.trapz(y=data[data.columns[0]], x=data.index)
            return integral
        else:
            raise NoBLMDataForIntensityInterval(
                '{} dataframe for given intensity interval is empty: {}'.format(col_name, blm_interval))

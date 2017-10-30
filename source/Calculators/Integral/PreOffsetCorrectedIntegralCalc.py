import numpy as np

from config import TIMBER_LOGGING_FREQ
from source.BLM_dose_calculation_exceptions import IntegrationResultBelowZero, IntensityIntervalNotCoveredByBLMData, \
    NoBLMDataForIntensityInterval, IntegrationResultIsNan
from source.Calculators.Integral.IntegralCalc import IntegralCalc


class PreOffsetCorrectedIntegralCalc(IntegralCalc):
    def run(self, data, blm_intervals):
        col_name = data.columns[0]
        for blm_interval in blm_intervals:
            blm_beam_on_data = blm_interval.get_integrated_data(data) - blm_interval.offset_pre
            try:
                integral_offset_corrected = self.__integrate(blm_beam_on_data, col_name, blm_interval)
            except (IntegrationResultBelowZero, IntensityIntervalNotCoveredByBLMData, IntegrationResultIsNan) as e:
                e.logging_func('{}'.format(str(e)))
                integral_offset_corrected = 0
            except NoBLMDataForIntensityInterval as e:
                if (blm_interval.end - blm_interval.start).total_seconds() > TIMBER_LOGGING_FREQ:
                    e.logging_func('{}'.format(str(e)))
            finally:
                blm_interval.integral_pre_offset_corrected = integral_offset_corrected

    def __integrate(self, data, col_name, blm_interval):
        if not data.empty:
            integral = np.trapz(y=data[data.columns[0]], x=data.index)
            if integral < 0:
                raise IntegrationResultBelowZero('{} integrated dose < 0: {}'.format(col_name, blm_interval))
            elif np.isnan(integral):
                IntegrationResultIsNan('{} integrated dose is Nan: {}'.format(col_name, blm_interval))
            return integral
        else:
            raise NoBLMDataForIntensityInterval(
                '{}\t{} dataframe for given intensity interval is empty: {}'.format(self.__class__.__name__,col_name, blm_interval))

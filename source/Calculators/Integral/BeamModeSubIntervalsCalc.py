import logging

import numpy as np
import pandas as pd
from configurations.config import TIMBER_LOGGING_FREQ
from source.BLM_dose_calculation_exceptions import IntegrationResultBelowZero, NoBLMDataForIntensitySubInterval, \
    IntegrationResultIsNan
from source.Calculators.Integral.IntegralCalc import IntegralCalc


class BeamModeSubIntervalsCalc(IntegralCalc):
    """
    The class which integrates a BLM data in subintervals (intervals split by beam mode changes). It also produces some extra BLM data (using the interpolation)
    in order to make the integration more accurate.
    """

    def run(self, data_old, blm_intervals):
        """
        The base class method implementation. See the IntegralCalc for the description.
        :param data:
        :param blm_intervals:
        :return:
        """
        col_name = data_old.columns[0]
        for blm_interval in blm_intervals:
            data = self.get_data_to_integrate(data_old, blm_interval)
            for subinterval in blm_interval.blm_subintervals:
                if blm_interval.integrated_dose_preoc == 0:
                    self.set_integration_result(subinterval, 0)
                else:
                    self.set_integration_result(subinterval, self.integrate_single_blm_interval(subinterval, data, col_name))


    def get_data_to_integrate(self, data, blm_interval):
        """
        The base class method implementation. See the IntegralCalc for the description.
        :param data:
        :param blm_interval:
        :return:
        """
        return data - blm_interval.offset_pre

    def integrate_single_blm_interval(self, subinterval, offset_corrected_data_for_blm_interval, blm_name):
        """
        The base class method implementation. See the IntegralCalc for the description.
        :param subinterval:
        :param offset_corrected_data_for_blm_interval:
        :param blm_name:
        :return:
        """
        integrated_dose = 0
        try:
            subinterval_data = subinterval.get_integrated_data(offset_corrected_data_for_blm_interval)
            integrated_dose = self.integrate(subinterval_data, blm_name, subinterval)
            self.check_if_integration_result_is_positive(integrated_dose, subinterval, blm_name)
        except (IntegrationResultBelowZero, IntegrationResultIsNan) as e:
            e.logging_func('{}\t{} {}'.format(self, blm_name, str(e)))
            integrated_dose = 0
        except NoBLMDataForIntensitySubInterval as e:
            if subinterval.get_duration() > TIMBER_LOGGING_FREQ:
                e.logging_func('{}\t{} {}'.format(self, blm_name, str(e)))
            integrated_dose = 0
        finally:
            return integrated_dose

    def set_integration_result(self, blm_subinterval, integration_result):
        """
        The base class method implementation. See the IntegralCalc for the description.
        :param blm_subinterval:
        :param integration_result:
        :return:
        """
        blm_subinterval.set_integration_result(integration_result)

    def integrate(self, data, col_name, blm_interval):
        """
        The base class method implementation. See the IntegralCalc for the description.
        :param data:
        :param col_name:
        :param blm_interval:
        :return:
        """
        if not data.empty:
            integral = np.trapz(y=data[data.columns[0]], x=data.index.astype(np.int64) / 10**9)
            if np.isnan(integral):
                IntegrationResultIsNan('{} integrated dose is Nan: {}'.format(col_name, blm_interval))
            return integral
        else:
            raise NoBLMDataForIntensitySubInterval(
                '{}\t{} dataframe for given intensity interval is empty: {}'.format(self,col_name, blm_interval))
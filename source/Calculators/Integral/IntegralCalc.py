from abc import abstractmethod

import sys

from source.Calculators.Calc import Calc
import numpy as np
from config import TIMBER_LOGGING_FREQ
from source.BLM_dose_calculation_exceptions import IntegrationResultBelowZero, NoBLMDataForIntensityInterval, IntegrationResultIsNan


class IntegralCalc(Calc):
    """
    Abstract class for all kinds of integrations. It iterates over BLM interval list, integrates and sets results.
    """
    def run(self, data, blm_intervals):
        """
        Iterates over blm_interval list.
        :param data:
        :param blm_intervals:
        :return:
        """
        # col_name = data.columns[0]
        col_name = str(blm_intervals[0].blm_name)
        for blm_interval in blm_intervals:
            blm_interval_beam_on_data = self.get_data_to_integrate(data, blm_interval)
            self.integrate_single_blm_interval(blm_interval, blm_interval_beam_on_data, col_name)

    def integrate_single_blm_interval(self, blm_interval, blm_interval_beam_on_data, blm_name):
        """
        Integrates one interval and sets a result.
        :param BLMInterval blm_interval:
        :param blm_interval_beam_on_data: data to be integrated (pandas dataframe of series)
        :param blm_name:
        :return:
        """
        integration_result = 0
        try:
            integration_result = self.integrate(blm_interval_beam_on_data, blm_name, blm_interval)
            self.check_if_integration_result_is_positive(integration_result, blm_interval, blm_name)
        except (IntegrationResultBelowZero, IntegrationResultIsNan) as e:
            e.logging_func('{}'.format(str(e)))
            integration_result = 0
        except NoBLMDataForIntensityInterval as e:
            if blm_interval.get_duration() > TIMBER_LOGGING_FREQ:
                e.logging_func('{}'.format(str(e)))
            integration_result = 0
        finally:
            self.set_integration_result(blm_interval, integration_result)

    def integrate(self, data, col_name, blm_interval):
        """
        Integrates data.
        :param data: data to be integrated
        :param col_name: name of the BLM
        :param blm_interval: BLM Interval
        :return:
        """
        if not data.empty:
            integral = np.trapz(y=data[data.columns[0]], x=data.index.astype(np.int64) / 10**9)
            if np.isnan(integral):
                IntegrationResultIsNan('{} integrated dose is Nan: {}'.format(col_name, blm_interval))
            return integral
        else:
            raise NoBLMDataForIntensityInterval(
                '{}\t{} dataframe for given intensity interval is empty: {}'.format(self, col_name, blm_interval))

    def check_if_integration_result_is_positive(self, integration_result, blm_interval, col_name):
        """
        Checks if integration result is >= 0. If no, raises IntegrationResultBelowZero exception.
        :param integration_result:
        :param blm_interval:
        :param col_name:
        :return:
        """
        if integration_result < 0:
            raise IntegrationResultBelowZero('{} integrated dose < 0: {}'.format(col_name, blm_interval))

    @abstractmethod
    def set_integration_result(self, blm_interval, integration_result):
        """
        Abstract method - it should assignees an integration result to blm_interval (or subinterval).
        :param blm_interval:
        :param integration_result:
        :return:
        """
        pass

    @abstractmethod
    def get_data_to_integrate(self, data, blm_interval):
        """
        Abstract method - it should return data prepared to integration.
        :param data:
        :param blm_interval:
        :return:
        """
        pass
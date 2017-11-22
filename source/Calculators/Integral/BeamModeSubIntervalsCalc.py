import logging

import numpy as np
import pandas as pd
from config import TIMBER_LOGGING_FREQ
from source.BLM_dose_calculation_exceptions import IntegrationResultBelowZero, NoBLMDataForIntensitySubInterval, \
    IntegrationResultIsNan
from source.Calculators.Integral.IntegralCalc import IntegralCalc
from source.Plotters.PlotCalc2 import PlotCalc


class BeamModeSubIntervalsCalc(IntegralCalc):
    """
    The class which integrates a BLM data in subintervals (intervals split by beam mode changes). It also produces some extra BLM data (using the interpolation)
    in order to make the integration more accurate.
    """
    # def fill_missing_integration_points(self, offset_corrected_data_for_blm_interval, new_indices):
    #     """
    #     Fill missing points. An intensity data were used to creation of subintervals. Due to the fact, that intensity data are stored with much higher frequency,
    #     beginnings and ends of subintervals don't covers with actual BLM data, so during integration it is possible to miss some dose.
    #     The goal is to add extra points to our data using interpolation. Extra points have timestamps equal to beginnings of subintervals, therefore during
    #     integration any small parts of subinterval won't be lost and the sum of doses in subintervals will be equal to the dose in the interval.
    #
    #     :param offset_corrected_data_for_blm_interval: Offset corrected data for a blm interval
    #     :param new_indices: start timestaps of subintervals
    #     :return:
    #     """
    #     # Adds starts of subintervals to our data
    #     new_data = pd.concat([offset_corrected_data_for_blm_interval, pd.DataFrame(index=new_indices)])
    #     # return new_data.fillna(0)
    #     # if only one readout is available, it can be assumed that dose is constant in our subinterval
    #     if len(offset_corrected_data_for_blm_interval.index) == 1:
    #         return new_data[~new_data.index.duplicated(keep='first')].sort_index().fillna(method='bfill').fillna(method='pad')
    #     # fills new added points with values using the linear interpolation
    #     elif len(offset_corrected_data_for_blm_interval.index) > 1:
    #         new_data = new_data[~new_data.index.duplicated(keep='first')].sort_index().interpolate(method='slinear').dropna()
    #         # new_data = new_data.sort_index().interpolate(method='slinear').dropna()
    #
    #         # new_data = new_data.fillna(0)
    #         # print(len(new_data), len(offset_corrected_data_for_blm_interval.index))
    #         return new_data
    #     return offset_corrected_data_for_blm_interval

    def run(self, data_old, blm_intervals):
        """
        The base class method implementation. See the IntegralCalc for the description.
        :param data:
        :param blm_intervals:
        :return:
        """
        # p = PlotCalc('/media/sf_monitoring_analysis/data/pickles/analysed_blm_2017_with_beam_mode2')
        col_name = data_old.columns[0]
        for blm_interval in blm_intervals:
            data = self.get_data_to_integrate(data_old, blm_interval)
            # if blm_interval.
            for subinterval in blm_interval.beam_modes_subintervals:
                self.integrate_single_blm_interval(subinterval, data, col_name)
            # p.run(data, [blm_interval])


    def get_data_to_integrate(self, data, blm_interval):
        """
        The base class method implementation. See the IntegralCalc for the description.
        :param data:
        :param blm_interval:
        :return:
        """
        return data - blm_interval.offset_pre
        # offset_corrected_data_for_blm_interval1 = data - blm_interval.offset_pre
        # prev_len = len(data.index)
        # timestamps = (sub.start for sub in blm_interval.beam_modes_subintervals)
        # offset_corrected_data_for_blm_interval = self.fill_missing_integration_points(offset_corrected_data_for_blm_interval1, timestamps)
        # logging.warning(str(len(offset_corrected_data_for_blm_interval.index) - prev_len))
        # return offset_corrected_data_for_blm_interval

    def integrate_single_blm_interval(self, subinterval, offset_corrected_data_for_blm_interval, blm_name):
        """
        The base class method implementation. See the IntegralCalc for the description.
        :param subinterval:
        :param offset_corrected_data_for_blm_interval:
        :param blm_name:
        :return:
        """
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
            self.set_integration_result(subinterval, integrated_dose)

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
            integral = np.trapz(y=data[data.columns[0]], x=data.index)
            if np.isnan(integral):
                IntegrationResultIsNan('{} integrated dose is Nan: {}'.format(col_name, blm_interval))
            return integral
        else:
            raise NoBLMDataForIntensitySubInterval(
                '{}\t{} dataframe for given intensity interval is empty: {}'.format(self,col_name, blm_interval))
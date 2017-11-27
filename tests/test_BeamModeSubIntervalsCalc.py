from unittest.mock import MagicMock, patch, call
import unittest

import numpy

from source.BLM_dose_calculation_exceptions import NoBLMDataForIntensitySubInterval, IntegrationResultIsNan, IntegrationResultBelowZero
from source.Calculators.Integral.BeamModeSubIntervalsCalc import BeamModeSubIntervalsCalc

class MyModelTestCase(unittest.TestCase):
    example_value = 502
    return_value = MagicMock()

    def setUp(self):
        blm_subinterval_11 = MagicMock(start=1, end=2, set_integration_result=MagicMock(), get_integrated_data=MagicMock())
        blm_subinterval_12 = MagicMock(start=2, end=2.5, set_integration_result=MagicMock(), get_integrated_data=MagicMock())
        blm_subinterval_13 = MagicMock(start=2.5, end=3, set_integration_result=MagicMock(), get_integrated_data=MagicMock())

        blm_subinterval_21 = MagicMock(start=4, end=4.2, set_integration_result=MagicMock(), get_integrated_data=MagicMock())
        blm_subinterval_22 = MagicMock(start=4.2, end=6, set_integration_result=MagicMock(), get_integrated_data=MagicMock())
        blm_subinterval_23 = MagicMock(start=6, end=7, set_integration_result=MagicMock(), get_integrated_data=MagicMock())
        blm_subinterval_24 = MagicMock(start=7, end=8, set_integration_result=MagicMock(), get_integrated_data=MagicMock())
        self.blm_interval_1 = MagicMock(start=1, end=3, integral_pre_offset_corrected=0, offset_pre=52, beam_modes_subintervals=[blm_subinterval_11, blm_subinterval_12, blm_subinterval_13])
        self.blm_interval_2 = MagicMock(start=4, end=8, integral_pre_offset_corrected=1.36,offset_pre=0.7, beam_modes_subintervals=[blm_subinterval_21, blm_subinterval_22, blm_subinterval_23, blm_subinterval_24])
        self.tested_object = BeamModeSubIntervalsCalc()

    @patch('source.Calculators.Integral.BeamModeSubIntervalsCalc.BeamModeSubIntervalsCalc.get_data_to_integrate')
    @patch('source.Calculators.Integral.BeamModeSubIntervalsCalc.BeamModeSubIntervalsCalc.integrate_single_blm_interval')
    def test_shouldSetIntegratedValueToZeroForAllSubintervals_ifBlmIntervalIntegratedDoseIsZero(self, mock_integrate_single_blm_interval, mock_get_data_to_integrate):

        tested_object = self.tested_object
        blm_intervals = [self.blm_interval_1]
        tested_object.run(MagicMock(), blm_intervals)

        blm_intervals[0].beam_modes_subintervals[0].set_integration_result.assert_called_with(0)
        blm_intervals[0].beam_modes_subintervals[1].set_integration_result.assert_called_with(0)
        blm_intervals[0].beam_modes_subintervals[2].set_integration_result.assert_called_with(0)

    @patch('source.Calculators.Integral.BeamModeSubIntervalsCalc.BeamModeSubIntervalsCalc.get_data_to_integrate')
    @patch('source.Calculators.Integral.BeamModeSubIntervalsCalc.BeamModeSubIntervalsCalc.integrate_single_blm_interval', return_value =example_value)
    def test_shouldSetIntegratedValueForAllSubintervals_ifBlmIntervalIntegratedDoseIsNotZero(self, mock_integrate_single_blm_interval, mock_get_data_to_integrate):
        tested_object = self.tested_object
        blm_intervals = [self.blm_interval_2]
        tested_object.run(MagicMock(), blm_intervals)

        integrated_value = self.example_value
        mock_get_data_to_integrate.return_value = integrated_value

        blm_intervals[0].beam_modes_subintervals[0].set_integration_result.assert_called_with(integrated_value)
        blm_intervals[0].beam_modes_subintervals[1].set_integration_result.assert_called_with(integrated_value)
        blm_intervals[0].beam_modes_subintervals[2].set_integration_result.assert_called_with(integrated_value)
        blm_intervals[0].beam_modes_subintervals[3].set_integration_result.assert_called_with(integrated_value)

    @patch('source.Calculators.Integral.BeamModeSubIntervalsCalc.BeamModeSubIntervalsCalc.get_data_to_integrate', return_value=return_value)
    @patch('source.Calculators.Integral.BeamModeSubIntervalsCalc.BeamModeSubIntervalsCalc.integrate_single_blm_interval')
    def test_shouldUseOffsetCorrectedData(self, mock_integrate_single_blm_interval, mock_get_data_to_integrate):
        tested_object = self.tested_object
        blm_intervals = [self.blm_interval_1, self.blm_interval_2]
        call1 = call(blm_intervals[1].beam_modes_subintervals[0], self.return_value, 'example name')
        call2 = call(blm_intervals[1].beam_modes_subintervals[1], self.return_value, 'example name')
        call3 = call(blm_intervals[1].beam_modes_subintervals[2], self.return_value, 'example name')
        call4 = call(blm_intervals[1].beam_modes_subintervals[3], self.return_value, 'example name')
        data = MagicMock(columns=['example name'])

        tested_object.run(data, blm_intervals)

        mock_get_data_to_integrate.assert_has_calls([call(data, blm_intervals[0]), call(data, blm_intervals[1])])

        mock_integrate_single_blm_interval.assert_has_calls([call1, call2, call3, call4], any_order=False)


    @patch('source.Calculators.Integral.BeamModeSubIntervalsCalc.BeamModeSubIntervalsCalc.integrate', side_effect=NoBLMDataForIntensitySubInterval('NoBLMDataForIntensitySubInterval'))
    def test_integrationOfSubintervalShouldReturnZero_ifNoData(self, mock_integrate):
        tested_object = self.tested_object
        blm_intervals = [self.blm_interval_2]
        subinterval = blm_intervals[0].beam_modes_subintervals[0]
        subinterval.get_duration.return_value = 0

        self.assertEqual(0, tested_object.integrate_single_blm_interval(subinterval, None, 'example name'))

    @patch('source.Calculators.Integral.BeamModeSubIntervalsCalc.BeamModeSubIntervalsCalc.integrate', side_effect=IntegrationResultIsNan('IntegrationResultIsNan'))
    def test_integrationOfSubintervalShouldReturnZero_ifIntegrationResultIsNan(self, mock_integrate):
        tested_object = self.tested_object
        blm_intervals = [self.blm_interval_2]
        subinterval = blm_intervals[0].beam_modes_subintervals[0]
        subinterval.get_duration.return_value = 0

        self.assertEqual(0, tested_object.integrate_single_blm_interval(subinterval, None, 'example name'))

    @patch('source.Calculators.Integral.BeamModeSubIntervalsCalc.BeamModeSubIntervalsCalc.integrate', side_effect=IntegrationResultBelowZero('IntegrationResultBelowZero'))
    def test_integrationOfSubintervalShouldReturnZero_ifIntegrationResultBelowZero(self, mock_integrate):
        tested_object = self.tested_object
        blm_intervals = [self.blm_interval_2]
        subinterval = blm_intervals[0].beam_modes_subintervals[0]
        subinterval.get_duration.return_value = 0

        self.assertEqual(0, tested_object.integrate_single_blm_interval(subinterval, None, 'example name'))

    @patch('source.Calculators.Integral.BeamModeSubIntervalsCalc.BeamModeSubIntervalsCalc.integrate', return_value=example_value)
    def test_integrationOfSubintervalShouldIntegrationResult_ifIntegrationResultValid(self, mock_integrate):
        tested_object = self.tested_object
        blm_intervals = [self.blm_interval_2]
        subinterval = blm_intervals[0].beam_modes_subintervals[0]
        subinterval.get_duration.return_value = 0
        subinterval.get_integrated_data.return_value = MagicMock()

        self.assertEqual(self.example_value, tested_object.integrate_single_blm_interval(subinterval, None, 'example name'))
        mock_integrate.assert_called_with(subinterval.get_integrated_data(), 'example name', subinterval)

    @patch('numpy.trapz', return_value=numpy.nan)
    def test_integrationOfSubintervalShouldRaiseExceptionIfNoData(self, mock_integrate):
        tested_object = self.tested_object
        blm_intervals = [self.blm_interval_2]
        subinterval = blm_intervals[0].beam_modes_subintervals[0]
        subinterval.get_duration.return_value = 0
        subinterval.get_integrated_data.return_value = MagicMock()

        self.assertEqual(self.example_value, tested_object.integrate_single_blm_interval(subinterval, None, 'example name'))
        mock_integrate.assert_called_with(subinterval.get_integrated_data(), 'example name', subinterval)

        # def integrate(self, data, col_name, blm_interval):
        #     """
        #     The base class method implementation. See the IntegralCalc for the description.
        #     :param data:
        #     :param col_name:
        #     :param blm_interval:
        #     :return:
        #     """
        #     if not data.empty:
        #         integral = np.trapz(y=data[data.columns[0]], x=data.index)
        #         if np.isnan(integral):
        #             IntegrationResultIsNan('{} integrated dose is Nan: {}'.format(col_name, blm_interval))
        #         return integral
        #     else:
        #         raise NoBLMDataForIntensitySubInterval(
        #             '{}\t{} dataframe for given intensity interval is empty: {}'.format(self, col_name, blm_interval))
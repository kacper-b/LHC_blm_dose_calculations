from source.Calculators.Integral.IntegralCalc import IntegralCalc


class PreOffsetCorrectedIntegralCalc(IntegralCalc):
    """
    Integrates data corrected using pre-offset.
    """
    def get_data_to_integrate(self, data, blm_interval):
        """
        The base class method implementation. See the IntegralCalc for the description.
        :param data:
        :param blm_interval:
        :return:
        """
        return blm_interval.get_integrated_data(data) - blm_interval.offset_pre

    def set_integration_result(self, blm_interval, integration_result):
        """
        The base class method implementation. See the IntegralCalc for the description.
        :param blm_interval:
        :param integration_result:
        :return:
        """
        blm_interval.integrated_dose_preoc = integration_result


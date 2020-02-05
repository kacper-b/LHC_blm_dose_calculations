from source.Calculators.Integral.IntegralCalc import IntegralCalc


class PostOffsetCorrectedIntegralCalc(IntegralCalc):
    """
    Integrates data corrected using post-offset.
    """
    def get_data_to_integrate(self, data, blm_interval):
        """
        The base class method implementation. See the IntegralCalc for the description.
        :param data:
        :param blm_interval:
        :return:
        """
        return blm_interval.get_integrated_data(data) - blm_interval.offset_post

    def set_integration_result(self, blm_interval, integration_result):
        """
        The base class method implementation. See the IntegralCalc for the description.
        :param blm_interval: BLM interval (or subinterval)
        :param integration_result:
        :return:
        """
        blm_interval.integrated_dose_postoc = integration_result

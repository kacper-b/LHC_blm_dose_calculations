from source.Calculators.Integral.IntegralCalc import IntegralCalc


class RawIntegralCalc(IntegralCalc):
    """
    Integrates raw data.
    """
    def run(self, data, blm_intervals):
        """
        The base class method implementation. See the IntegralCalc for the description.
        :param data:
        :param blm_intervals:
        :return:
        """
        col_name = data.columns[0]
        for blm_interval in blm_intervals:
            blm_beam_on_data = self.get_data_to_integrate(data, blm_interval)
            self.integrate_single_blm_interval(blm_interval, blm_beam_on_data, col_name)

    def get_data_to_integrate(self, data, blm_interval):
        """
        The base class method implementation. See the IntegralCalc for the description.
        :param data:
        :param blm_interval:
        :return:
        """
        return blm_interval.get_integrated_data(data)

    def set_integration_result(self, blm_interval, integration_result):
        """
        The base class method implementation. See the IntegralCalc for the description.
        :param blm_interval:
        :param integration_result:
        :return:
        """
        blm_interval.integrated_dose = integration_result

    def check_if_integration_result_is_positive(self, integration_result, blm_interval, col_name):
        """
        The base class method implementation. See the IntegralCalc for the description.
        :param integration_result:
        :param blm_interval:
        :param col_name:
        :return:
        """
        pass # It does nothing when the integration_result < 0

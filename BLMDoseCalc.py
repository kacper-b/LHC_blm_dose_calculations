import numpy as np

from source.BLM_dose_calculation_exceptions import *


class BLMDoseCalc:
    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.intensity_intervals = None
        self.offset_pre = 0
        self.offset_post = 0

    def integrate_over_intensity_interval(self, intensity_interval):
        try:
            offset_pre, _ = self.offset_calc_pre(intensity_interval)
        except (PreOffsetEmpty, PreOffsetBelowZero, PreOffsetNan) as e:
            offset_pre = 0
            # print(e)

        try:
            offset_post, _ = self.offset_calc_post(intensity_interval)
        except (PostOffsetEmpty, PostOffsetNan, PostOffsetBelowZero) as e:
            offset_post = 0
            # print(e)

        blm_beam_on_data = self.data[
            (intensity_interval.start <= self.data.index) & (self.data.index <= intensity_interval.end)]

        try:
            integration_result_pre_oc = self.__integrate_oc(intensity_interval, blm_beam_on_data - offset_pre)

        except (IntegrationResultBelowZero, IntensityIntervalNotCoveredByBLMData, NoBLMDataForIntensityInterval) as e:
            # print(e)
            integration_result_pre_oc = 0
            pass

        try:
            integration_result_post_oc = self.__integrate_oc(intensity_interval, blm_beam_on_data - offset_post)

        except (IntegrationResultBelowZero, IntensityIntervalNotCoveredByBLMData, NoBLMDataForIntensityInterval) as e:
            # print(e)
            integration_result_post_oc = 0
            pass

        return integration_result_pre_oc

    def __integrate_oc(self, intensity_interval, data):
        if not data.empty:
            integral = np.trapz(y=data[data.columns[0]], x=data.index)
            if integral < 0:
                raise IntegrationResultBelowZero('{} integrated dose < 0: {}'.format(self.name, intensity_interval))
            return integral
        else:
            raise NoBLMDataForIntensityInterval(
                '{} dataframe for given intensity interval is empty: {}'.format(self.name, intensity_interval))

    def offset_calc_pre(self, intensity_interval, offset_sec=5 * 60):
        offset_period = (self.data.index >= (intensity_interval.start - offset_sec)) & (
            self.data.index <= intensity_interval.start)
        offset_interval_pre = self.data[offset_period]

        if not offset_interval_pre.empty:
            offset = np.mean(offset_interval_pre[self.name])
            if not np.isnan(offset):
                return offset, offset_interval_pre
            else:
                raise PreOffsetNan('{} pre-offset dataframe is empty: {}'.format(self.name, intensity_interval))
        else:
            raise PreOffsetEmpty('{} pre-offset dataframe is empty: {}'.format(self.name, intensity_interval))

    def offset_calc_post(self, intensity_interval, offset_sec=5 * 60):
        offset_period = (self.data.index >= intensity_interval.end) & (
            self.data.index <= intensity_interval.end + offset_sec)
        offset_interval_post = self.data[offset_period]

        if not offset_interval_post.empty:
            offset = np.mean(offset_interval_post[self.name])
            if not np.isnan(offset):
                return offset, offset_interval_post
            else:
                raise PostOffsetNan('Post-offset value is Nan: {} {}'.format(self.name, intensity_interval))
        else:
            raise PostOffsetEmpty('Post-offset dataframe is empty: {} {}'.format(self.name, intensity_interval))

    def plot(self):
        pass

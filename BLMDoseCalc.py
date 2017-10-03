import numpy as np
from BLM_dose_calculation_exceptions import *


class BLMDoseCalc:
    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.intensity_intervals = None
        self.offset_pre = 0
        self.offset_post = 0

    def integrate_over_intensity_interval(self, intensity_interval):
        integration_result, integration_result_pre_oc = 0, 0
        try:
            blm_beam_on_data = self.data[(intensity_interval.start <= self.data.index) & (self.data.index <= intensity_interval.end)]
            offset_pre,_ = self.offset_calc_pre(intensity_interval)
            offset_post,_ = self.offset_calc_post(intensity_interval)

            integration_result_pre_oc = self.__integrate_oc(intensity_interval, blm_beam_on_data - offset_pre)
            integration_result = self.__integrate(intensity_interval)

            rst = integration_result - offset_pre * (min(intensity_interval.end, blm_beam_on_data.index[-1]) - max(intensity_interval.start, blm_beam_on_data.index[0]))
            rst = rst if rst >0 else 0
            eq = abs(rst - integration_result_pre_oc) < 1e-15
            if not eq:
                print(rst- integration_result_pre_oc)
        except (IntegrationResultBelowZero, IntensityIntervalNotCoveredByBLMData,
                NoBLMDataForIntensityInterval, PreOffsetEmpty, PostOffsetNan, PreOffsetNan,
                PostOffsetEmpty, PreOffsetBelowZero, PostOffsetBelowZero) as e:
            # print(e)
            pass
        else:
            pass

        return integration_result

    def __integrate(self, intensity_interval):
        beam_period = (intensity_interval.start <= self.data.index) & (self.data.index <= intensity_interval.end)
        data = self.data[beam_period]

        # is_whole_period_covered_by_data = (intensity_interval.start >= self.data.index[0]) & (self.data.index[-1] >= intensity_interval.end)

        if not data.empty:# and is_whole_period_covered_by_data:
            integral = np.trapz(y=data[data.columns[0]], x=data.index)
            # if integral < 0:
            #     raise IntegrationResultBelowZero('{} integrated dose < 0: {}'.format(self.name, intensity_interval))
            return integral

        # elif not is_whole_period_covered_by_data:
        #     raise IntensityIntervalNotCoveredByBLMData('intensity interval does not cover {}: {}'.format(self.name, intensity_interval))
        else:
            raise NoBLMDataForIntensityInterval('{} dataframe for given intensity interval is empty: {}'.format(self.name, intensity_interval))

    def __integrate_oc(self, intensity_interval, data):
        if not data.empty:# and is_whole_period_covered_by_data:
            integral = np.trapz(y=data[data.columns[0]], x=data.index)
            if integral < 0:
                raise IntegrationResultBelowZero('{} integrated dose < 0: {}'.format(self.name, intensity_interval))
            return integral
        else:
            raise NoBLMDataForIntensityInterval('{} dataframe for given intensity interval is empty: {}'.format(self.name, intensity_interval))


    def offset_calc_pre(self, intensity_interval, offset_sec=5 * 60):
        offset_period = (self.data.index >= (intensity_interval.start - offset_sec)) & (self.data.index <= intensity_interval.start)
        offset_interval_pre = self.data[offset_period]

        if not offset_interval_pre.empty:
            offset = np.mean(offset_interval_pre[self.name])
            if not np.isnan(offset):
                # if offset < 0:
                #     raise PreOffsetBelowZero('{} pre-offset dataframe is empty: {}'.format(self.name, intensity_interval))
                return offset, offset_interval_pre
            else:
                raise PreOffsetNan('{} pre-offset dataframe is empty: {}'.format(self.name, intensity_interval))
        else:
            raise PreOffsetEmpty('{} pre-offset dataframe is empty: {}'.format(self.name, intensity_interval))

    def offset_calc_post(self, intensity_interval, offset_sec=5 * 60):
        offset_period = (self.data.index >= intensity_interval.end) & (self.data.index <= intensity_interval.end + offset_sec)
        offset_interval_post = self.data[offset_period]

        if not offset_interval_post.empty:
            offset = np.mean(offset_interval_post[self.name])
            if not np.isnan(offset):
                # if offset < 0:
                #     raise PostOffsetBelowZero('Post-offset value is < 0: {} {}'.format(self.name, intensity_interval))
                return offset, offset_interval_post
            else:
                raise PostOffsetNan('Post-offset value is Nan: {} {}'.format(self.name, intensity_interval))
        else:
            raise PostOffsetEmpty('Post-offset dataframe is empty: {} {}'.format(self.name, intensity_interval))

    def plot(self):
        pass
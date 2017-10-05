import numpy as np

from source.BLM_dose_calculation_exceptions import PostOffsetNan, PostOffsetEmpty, PostOffsetNotSetDueToNeighbourhood
from source.Calculators.Offset.OffsetCalc import OffsetCalc


class PostOffsetCalc(OffsetCalc):
    def __init__(self, offset_sec=5 * 60):
        self.offset_sec = offset_sec

    def run(self, data, blm_intervals):
        col_name = data.columns[0]
        offset = 0
        offset_start = data.index[-1]
        offset_end = data.index[-1]
        for i, blm_interval in enumerate(reversed(blm_intervals)):
            i = len(blm_intervals) - i -1
            try:
                offset_period = self.__get_offset_period(blm_intervals, col_name, data, i)
                offset_data = data[offset_period]
                offset = self.__find_offset(offset_data, col_name, blm_interval)
                offset_start = offset_data.index[0]
                offset_end = offset_data.index[-1]
            except (PostOffsetNan, PostOffsetEmpty, PostOffsetNotSetDueToNeighbourhood) as e:
                # print(e)
                pass
            finally:
                blm_interval.offset_post = offset
                blm_interval.offset_post_start = offset_start
                blm_interval.offset_post_end = offset_end

    def __get_offset_period(self, blm_intervals, col_name, data, i):
        is_interval_after_current = (i + 1) < len(blm_intervals)
        is_enough_data_after = (data.index[-1] - blm_intervals[i].end) > self.offset_sec
        is_enough_space_between_next_interval = is_interval_after_current and (blm_intervals[i + 1].start - blm_intervals[i].end) > self.offset_sec
        is_enough_data_before = False
        is_enough_space_between_prev_interval = False
        if not (is_enough_data_after and is_enough_space_between_next_interval):
            is_enough_data_before = (blm_intervals[i].start - data.index[0]) >= self.offset_sec
            is_enough_space_between_prev_interval = (blm_intervals[i].start - blm_intervals[
                i - 1].end) >= self.offset_sec

        if is_enough_data_after and is_enough_space_between_next_interval:
            return (data.index > blm_intervals[i].end) & (data.index <= blm_intervals[i].end + self.offset_sec)
        elif is_enough_data_before and is_enough_space_between_prev_interval:
            return (data.index >= (blm_intervals[i].start - self.offset_sec)) & (data.index < blm_intervals[i].start)

        else:
            raise PostOffsetNotSetDueToNeighbourhood(
                '{} Post-offset neighbourhood is too small: {}'.format(col_name, blm_intervals[i]))

    def __find_offset(self, offset_data, col_name, blm_interval):
        if not offset_data.empty:
            offset = np.average(offset_data[col_name])
            if not np.isnan(offset):
                return offset
            else:
                raise PostOffsetNan('{} Post-offset value is Nan: {}'.format(col_name, blm_interval))
        else:
            raise PostOffsetEmpty('{} post-offset dataframe is empty: {}'.format(col_name, blm_interval))



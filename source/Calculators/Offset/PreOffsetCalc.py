import numpy as np

from source.BLM_dose_calculation_exceptions import PreOffsetNan, PreOffsetEmpty, PreOffsetNotSetDueToNeighbourhood, \
    PreOffsetStdevOverThreshold
from source.Calculators.Offset.OffsetCalc import OffsetCalc
import pandas as pd

class PreOffsetCalc(OffsetCalc):
    def __init__(self, offset_sec=5 * 60, std_dev_threshold=0.5):
        self.offset_sec = offset_sec
        self.std_dev_threshold = std_dev_threshold

    def run(self, data, blm_intervals):
        col_name = data.columns[0]
        offset = 0
        offset_start = data.index[0]
        offset_end = data.index[0]
        for i, blm_interval in enumerate(blm_intervals):
            try:
                offset_period = self.__get_offset_period(blm_intervals, col_name, data, i)
                offset_data = data[offset_period]
                offset = self.__find_offset(offset_data, col_name, blm_interval)
            except PreOffsetStdevOverThreshold as e:
                print(e)
            except (PreOffsetNan, PreOffsetEmpty, PreOffsetNotSetDueToNeighbourhood) as e:
                # print(e)
                pass
            finally:
                blm_interval.offset_pre = offset
                blm_interval.offset_pre_start = offset_start
                blm_interval.offset_pre_end = offset_end

    def __get_offset_period(self, blm_intervals, col_name, data, i):
        is_enough_data_before = (blm_intervals[i].start - data.index[0]) > self.offset_sec
        is_enough_space_between_prev_interval = (blm_intervals[i].start - blm_intervals[i - 1].end) > self.offset_sec
        is_enough_data_after = False
        is_enough_space_between_next_interval = False
        if not (is_enough_data_before and is_enough_space_between_prev_interval):
            is_interval_after_current = (i + 1) < len(blm_intervals)
            is_enough_data_after = (data.index[-1] - blm_intervals[i].end) > self.offset_sec
            is_enough_space_between_next_interval = is_interval_after_current and \
                                                (blm_intervals[i + 1].start -blm_intervals[i].end) > self.offset_sec
        if is_enough_data_before and is_enough_space_between_prev_interval:
            return (data.index >= (blm_intervals[i].start - self.offset_sec)) & (data.index < blm_intervals[i].start)
        elif is_enough_data_after and is_enough_space_between_next_interval:
            return (data.index > blm_intervals[i].end) & (data.index <= blm_intervals[i].end + self.offset_sec)
        else:
            raise PreOffsetNotSetDueToNeighbourhood(
                '{} PreOffset neighbourhood is too small:\n\tinterval: {}'.format(col_name, blm_intervals[i]))

    def __find_offset(self, offset_pandas_df, col_name, blm_interval):
        if not offset_pandas_df.empty:
            offset_data = offset_pandas_df[col_name].values
            offset = np.average(offset_data)
            if not np.isnan(offset):
                if self.__is_stdev_lower_than_threshold(offset_data, offset):
                    return offset
                else:
                    offset_data_without_biggest_value = self.__drop_the_biggest_abs_value(offset_data)
                    offset = np.average(offset_data_without_biggest_value)
                    if self.__is_stdev_lower_than_threshold(offset_data_without_biggest_value, offset):
                        return offset
                    else:
                        raise PreOffsetStdevOverThreshold('{} PreOffset data stdev {:.0%} > {:.0%} {} {}:\n\tinterval: {}'.
                              format(col_name,
                                     offset/np.average(offset_data_without_biggest_value),
                                     self.std_dev_threshold,
                                     len(offset_data),
                                     len(offset_data_without_biggest_value), blm_interval))
            else:
                raise PreOffsetNan('{} PreOffset is Nan:\n\tinterval: {}'.format(col_name, blm_interval))
        else:
            raise PreOffsetEmpty('{} PreOffset dataframe is empty:\n\tinterval: {}'.format(col_name, blm_interval))

    def __drop_the_biggest_abs_value(self, data):
        max_index = np.argmax(np.abs(data), axis=0)
        return np.concatenate((data[:max_index], data[max_index+1:]))

    def __is_stdev_lower_than_threshold(self, data, average):
        return np.std(data)/average < self.std_dev_threshold


if __name__  == '__main__':
    calc = PreOffsetCalc()
    print(calc._PreOffsetCalc__drop_the_biggest_abs_value(np.array([-65,1,2,3,4])))
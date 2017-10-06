import numpy as np

from source.BLM_dose_calculation_exceptions import PreOffsetNan, PreOffsetEmpty, PreOffsetNotSetDueToNeighbourhood, PreOffsetStdevOverThreshold
from source.Calculators.Offset.OffsetCalc import OffsetCalc

class PreOffsetCalc(OffsetCalc):
    def __init__(self, offset_sec=5 * 60, std_dev_threshold=0.5):
        self.offset_sec = offset_sec
        self.std_dev_threshold = std_dev_threshold

    def run(self, data, blm_intervals):
        col_name = data.columns[0]
        current_offset_val = 0
        offset_period_start = data.index[0]
        offset_period_end = data.index[0]
        for current_blm_idx in range(len(blm_intervals)):
            current_offset_val, offset_period_start, offset_period_end = self.fill_interval_with_pre_offset(blm_intervals, col_name, current_blm_idx,
                                                                                                            current_offset_val, data, offset_period_start,
                                                                                                            offset_period_end)

    def fill_interval_with_pre_offset(self, blm_intervals, col_name, current_blm_idx, current_offset_val, data, offset_period_start, offset_period_end):
        try:
            offset_period = self.__get_offset_period(blm_intervals, col_name, data, current_blm_idx)
            offset_data = data[offset_period]
            current_offset_val = self.__find_offset(offset_data, col_name, blm_intervals[current_blm_idx])
            offset_period_start = offset_data.index[0]
            offset_period_end = offset_data.index[-1]
        except PreOffsetStdevOverThreshold as e:
            # print(e)
            blm_intervals[current_blm_idx].is_suspected = True
            pass
        except (PreOffsetNan, PreOffsetEmpty, PreOffsetNotSetDueToNeighbourhood) as e:
            # print(e)
            blm_intervals[current_blm_idx].is_suspected = True
            pass
        finally:
            blm_intervals[current_blm_idx].offset_pre = current_offset_val
            blm_intervals[current_blm_idx].offset_pre_start = offset_period_start
            blm_intervals[current_blm_idx].offset_pre_end = offset_period_end
            return current_offset_val, offset_period_start, offset_period_end

    def __get_offset_period(self, blm_intervals, col_name, data, current_blm_idx):
        is_enough_data_before = (blm_intervals[current_blm_idx].start - data.index[0]) > self.offset_sec
        is_enough_space_between_prev_interval = (blm_intervals[current_blm_idx].start - blm_intervals[current_blm_idx - 1].end) > self.offset_sec
        is_enough_data_after = None
        is_enough_space_between_next_interval = None

        # if the interval beginning is too close to the beginning of data or to a previous interval check if there is enough space after the interval
        if not (is_enough_data_before and is_enough_space_between_prev_interval):
            is_any_interval_after_current = (current_blm_idx + 1) < len(blm_intervals)
            is_enough_data_after = (data.index[-1] - blm_intervals[current_blm_idx].end) > self.offset_sec
            is_enough_space_between_next_interval = is_any_interval_after_current and \
                                                    (blm_intervals[current_blm_idx + 1].start - blm_intervals[current_blm_idx].end) > self.offset_sec

        if is_enough_data_before and is_enough_space_between_prev_interval:
            return (data.index >= (blm_intervals[current_blm_idx].start - self.offset_sec)) & (data.index < blm_intervals[current_blm_idx].start)
        elif is_enough_data_after and is_enough_space_between_next_interval:
            return (data.index > blm_intervals[current_blm_idx].end) & (data.index <= blm_intervals[current_blm_idx].end + self.offset_sec)
        else:
            raise PreOffsetNotSetDueToNeighbourhood('{} PreOffset neighbourhood is too small:\n\tinterval: {}'.format(col_name, blm_intervals[current_blm_idx]))

    def __find_offset(self, offset_pandas_df, col_name, blm_interval):
        if not offset_pandas_df.empty:
            offset_data = offset_pandas_df[col_name].values
            offset = np.average(offset_data)
            if not np.isnan(offset):
                if self.__is_stdev_lower_than_threshold(offset_data, offset):
                    return offset
                else:
                    return self.remove_the_biggest_value_and_try_again(offset_data, blm_interval, col_name)
            else:
                raise PreOffsetNan('{} PreOffset is Nan:\n\tinterval: {}'.format(col_name, blm_interval))
        else:
            raise PreOffsetEmpty('{} PreOffset dataframe is empty:\n\tinterval: {}'.format(col_name, blm_interval))

    def remove_the_biggest_value_and_try_again(self, offset_data, blm_interval, col_name):
        offset_data_without_biggest_value = self.__drop_the_biggest_abs_value(offset_data)
        offset = np.average(offset_data_without_biggest_value)
        if self.__is_stdev_lower_than_threshold(offset_data_without_biggest_value, offset):
            return offset
        else:
            raise PreOffsetStdevOverThreshold(self.__get_stdev_over_threshold_exeption_description(blm_interval, col_name, offset, offset_data_without_biggest_value))

    def __get_stdev_over_threshold_exeption_description(self, blm_interval, col_name, offset, offset_data_without_biggest_value):
        return '{} PreOffset data stdev {:.0%} > {:.0%}:\n\tinterval: {}'.format(col_name, offset / np.average(offset_data_without_biggest_value),
                                                                                 self.std_dev_threshold, blm_interval)

    def __drop_the_biggest_abs_value(self, data):
        max_index = np.argmax(np.abs(data), axis=0)
        return np.concatenate((data[:max_index], data[max_index+1:]))

    def __is_stdev_lower_than_threshold(self, data, average):
        return np.std(data)/average < self.std_dev_threshold


if __name__  == '__main__':
    calc = PreOffsetCalc()
    print(calc._PreOffsetCalc__drop_the_biggest_abs_value(np.array([-65,1,2,3,4])))
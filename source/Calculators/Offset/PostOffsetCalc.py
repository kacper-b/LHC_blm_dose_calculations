import numpy as np

from source.BLM_dose_calculation_exceptions import PostOffsetNan, PostOffsetEmpty, PostOffsetNotSetDueToNeighbourhood, \
    PostOffsetStdevOverThreshold, PreOffsetEmpty
from source.Calculators.Offset.OffsetCalc import OffsetCalc


class PostOffsetCalc(OffsetCalc):
    def __init__(self, offset_length=5 * 60, post_offset_shift=85, std_dev_threshold=0.5):
        self.offset_length = offset_length
        self.post_offset_shift = post_offset_shift
        self.std_dev_threshold = std_dev_threshold

    def run(self, data, blm_intervals):
        col_name = data.columns[0]
        current_offset_val = 0
        offset_period_start = data.index[0]
        offset_period_end = data.index[0]
        for current_blm_idx in range(len(blm_intervals)-1,-1, -1):
            current_offset_val, offset_period_start, offset_period_end = self.__fill_interval_with_post_offset(blm_intervals, col_name, current_blm_idx,
                                                                                                               current_offset_val, data, offset_period_start,
                                                                                                               offset_period_end)

    def __fill_interval_with_post_offset(self, blm_intervals, col_name, current_blm_idx, current_offset_val, data, offset_period_start, offset_period_end):
        try:
            offset_period = self.__get_offset_period(blm_intervals, col_name, data, current_blm_idx)
            offset_data = data[offset_period]
            current_offset_val = self.__find_offset(offset_data, col_name, blm_intervals[current_blm_idx])
            offset_period_start = offset_data.index[0]
            offset_period_end = offset_data.index[-1]
        except (PostOffsetNan, PostOffsetEmpty, PostOffsetNotSetDueToNeighbourhood) as e:
            # print(e)
            pass
        except PostOffsetStdevOverThreshold as e:
            # print(e)
            pass
        finally:
            blm_intervals[current_blm_idx].offset_post = current_offset_val
            blm_intervals[current_blm_idx].offset_post_start = offset_period_start
            blm_intervals[current_blm_idx].offset_post_end = offset_period_end
            return current_offset_val, offset_period_start, offset_period_end

    def __get_offset_period(self, blm_intervals, col_name, data, current_blm_idx):
        """

        :param blm_intervals:
        :param col_name:
        :param data:
        :param current_blm_idx:
        :return:
        """
        # START: definitions of variables
        interval_start = blm_intervals[current_blm_idx].start
        interval_end = blm_intervals[current_blm_idx].end

        post_offset_period_start = interval_end + self.post_offset_shift
        post_offset_period_end = post_offset_period_start + self.offset_length

        pre_offset_period_start = interval_start - self.offset_length
        pre_offset_period_end = interval_start

        available_data_end = data.index[-1]
        next_blm_idx = current_blm_idx + 1

        is_enough_data_after = post_offset_period_end < available_data_end
        is_it_the_first_interval = current_blm_idx == 0
        is_interval_after_current = next_blm_idx < len(blm_intervals)
        is_enough_space_between_next_interval = (is_interval_after_current and post_offset_period_end < blm_intervals[next_blm_idx].start) or not is_interval_after_current
        is_enough_data_before = None
        is_enough_space_between_prev_interval = None
        # END: definitions of variables

        # if the interval beginning is too close to the beginning of data or to a previous interval check if there is enough space after the interval
        if not (is_enough_data_after and is_enough_space_between_next_interval):
            available_data_start = data.index[0]
            previous_blm_idx = current_blm_idx - 1

            is_enough_data_before = available_data_start <= pre_offset_period_start
            is_enough_space_between_prev_interval = is_it_the_first_interval or blm_intervals[previous_blm_idx].end <= pre_offset_period_start

        if is_enough_data_after and is_enough_space_between_next_interval:
            return (post_offset_period_start < data.index) & (data.index <= post_offset_period_end)

        elif is_enough_data_before and is_enough_space_between_prev_interval:
            return (pre_offset_period_start <= data.index) & (data.index < pre_offset_period_end)

        else:
            raise PostOffsetNotSetDueToNeighbourhood('{} PostOffset neighbourhood is too small: {}'.format(col_name, blm_intervals[current_blm_idx]))


    def __find_offset(self, offset_pandas_df, col_name, blm_interval):
        if not offset_pandas_df.empty:
            offset_data = offset_pandas_df[col_name].values
            offset = np.average(offset_data)
            if not np.isnan(offset):
                if self.__is_stdev_lower_than_threshold(offset_data, offset):
                    return offset
                else:
                    return self.__remove_the_biggest_value_and_check_stdev_again(offset_data, blm_interval, col_name)
            else:
                raise PostOffsetNan('{} PostOffset is Nan:\n\tinterval: {}'.format(col_name, blm_interval))
        else:
            raise PostOffsetEmpty('{} PostOffset dataframe is empty:\n\tinterval: {}'.format(col_name, blm_interval))

    def __get_stdev_over_threshold_exception_description(self, blm_interval, col_name, offset, offset_data_without_biggest_value):
        return '{} PostOffset data stdev {:.0%} > {:.0%}:\n\tinterval: {}'.format(col_name, offset / np.average(offset_data_without_biggest_value),
                                                                                  self.std_dev_threshold, blm_interval)

    def __drop_the_biggest_abs_value(self, data):
        max_index = np.argmax(np.abs(data), axis=0)
        return np.concatenate(data[:max_index], data[max_index+1:])

    def __is_stdev_lower_than_threshold(self, data, average):
        return np.std(data)/average < self.std_dev_threshold

    def __remove_the_biggest_value_and_check_stdev_again(self, offset_data, blm_interval, col_name):
        offset_data_without_biggest_value = self.__drop_the_biggest_abs_value(offset_data)
        offset = np.average(offset_data_without_biggest_value)
        if self.__is_stdev_lower_than_threshold(offset_data_without_biggest_value, offset):
            return offset
        else:
            raise PostOffsetStdevOverThreshold(self.__get_stdev_over_threshold_exception_description(blm_interval, col_name, offset,
                                                                                                     offset_data_without_biggest_value))

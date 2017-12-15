from abc import abstractmethod, abstractproperty

from source.Calculators.Calc import Calc
import numpy as np

class OffsetCalc(Calc):
    """
    Abstract class - inheriting classes should calculate an offset.
    """
    @property
    @abstractmethod
    def OffsetNan(self):
        """
        In a child class that property should be assigned with an exception that occurs when the calculated offset is Nan.
        """
        pass

    @property
    @abstractmethod
    def OffsetEmpty(self):
        """
        In a child class that property should be assigned with an exception that occurs when the data used to an offset calculation is empty.
        """
        pass

    @property
    @abstractmethod
    def OffsetStdevOverThreshold(self):
        """
        In a child class that property should be assigned with an exception that occurs when the data's standard deviation is above a threshold.
        """
        pass

    @property
    @abstractmethod
    def OffsetNotSetDueToNeighbourhood(self):
        """
        In a child class that property should be assigned with an exception that occurs when the data used to an offset calculation is not huge enough.
        It can happen when a required offset range is not covered by a BLM data or when it consists a period when the beam was on.
        """
        pass

    @property
    @abstractmethod
    def blm_interval_offset_fields(self):
        """
        In a child class that property should be assigned with a dict which maps variables used in this class onto fields in an BLM interval:
        Example (for post-offset):
        {'offset':None, 'offset_start':None, 'offset_end':None} --> {'offset': 'offset_post', 'offset_start': 'offset_post_start', 'offset_end': 'offset_post_end'}
        """
        return {'offset':None, 'offset_start':None, 'offset_end':None}

    @abstractmethod
    def get_blm_intervals_iterator(self, blm_intervals):
        """
        It returns iterator which provides blm_intervals' indices in a needed order.
        :param blm_intervals: iterable BLM intervals' collection
        :return:
        """
        pass

    @abstractmethod
    def get_offset_period(self, blm_intervals, col_name, data, current_blm_interval_idx):
        """
        Finds and returns bool mask for a given data. True values are assignees to data points which are used to (pre-/post-)offset calculation.
        :param blm_intervals: all intervals for the current BLM
        :param col_name: BLM name (column name in a BLM data)
        :param data: BLM data
        :param current_blm_interval_idx:
        :return:
        """
        pass

    def __init__(self, offset_length=5 * 60, post_offset_shift=85, std_dev_threshold=0.5):
        """
        Initializes the offset calculator with calculations' parameters.
        :param offset_length: an offset period's duration - in seconds
        :param post_offset_shift: a post offset's delay. If a post offset calculation is needed, the offset's beginning range would be delayed
         #post_offset_shift seconds (with reference to the end of a BLM interval)
        :param std_dev_threshold: offset's standard deviation relative value - if an offset data have a higher stddev, exception will occur.
        """
        self.offset_length = offset_length
        self.post_offset_shift = post_offset_shift
        self.std_dev_threshold = std_dev_threshold

    def fill_interval_with_offset(self, blm_intervals, col_name, current_blm_interval_idx, current_offset_val, data, offset_period_start, offset_period_end):
        """
        Tries to calculate offset for the interval with given index. If it is not possible, sets offset from the previous interval.
        :param blm_intervals: all intervals for the current BLM
        :param col_name: BLM name (column name in a BLM data)
        :param current_blm_interval_idx: index of the currently analysed BLM interval
        :param current_offset_val: current offset value
        :param data: BLM data
        :param offset_period_start: timestamp of the start of an offset period - in seconds since the epoch.
        :param offset_period_end: timestamp of the end of an offset period - in seconds since the epoch.
        :return:
        """
        try:
            offset_period = self.get_offset_period(blm_intervals, col_name, data, current_blm_interval_idx)
            offset_data = data[offset_period]
            current_offset_val = self.find_offset(offset_data, col_name, blm_intervals[current_blm_interval_idx])
            offset_period_start = offset_data.index[0]
            offset_period_end = offset_data.index[-1]
        except self.OffsetNotSetDueToNeighbourhood as e:
            e.logging_func('{}'.format(str(e)))
            blm_intervals[current_blm_interval_idx].should_plot = True
            pass
        except (self.OffsetNan, self.OffsetEmpty, self.OffsetNotSetDueToNeighbourhood) as e:
            e.logging_func('{}'.format(str(e)))
            blm_intervals[current_blm_interval_idx].should_plot = True
            pass
        finally:
            # Assigns offset to the blm_interval.
            setattr(blm_intervals[current_blm_interval_idx], self.blm_interval_offset_fields['offset'], current_offset_val)
            setattr(blm_intervals[current_blm_interval_idx], self.blm_interval_offset_fields['offset_start'], offset_period_start)
            setattr(blm_intervals[current_blm_interval_idx], self.blm_interval_offset_fields['offset_end'], offset_period_end)
            return current_offset_val, offset_period_start, offset_period_end

    def run(self, data, blm_intervals):
        """
        Iterates over blm_intervals and sets offset fields. If it's not possible to calculate an offset, keep the old one
        (in the beginning the old offset is equal 1).
        :param data:
        :param blm_intervals:
        :return:
        """
        col_name = data.columns[0]
        current_offset_val = 0
        offset_period_start = data.index[0]
        offset_period_end = data.index[0]
        for current_blm_interval_idx in self.get_blm_intervals_iterator(blm_intervals):
            current_offset_val, offset_period_start, offset_period_end = self.fill_interval_with_offset(blm_intervals, col_name, current_blm_interval_idx,
                                                                                                            current_offset_val, data, offset_period_start,
                                                                                                            offset_period_end)

    def is_stdev_lower_than_threshold(self, data, average):
        """
        Checks if standard deviation is below the threshold.
        :param data:
        :param float average:
        :return bool:
        """
        return np.std(data) / average < self.std_dev_threshold

    def drop_the_biggest_abs_value(self, data):
        """
        Removes the value, which has the biggest absolute value.
        :param data:
        :return: data without a value with the biggest absolute value.
        """
        max_index = np.argmax(np.abs(data), axis=0)
        return np.concatenate((data[:max_index], data[max_index+1:]))

    def get_stdev_over_threshold_exception_description(self, blm_interval, col_name, offset, offset_data_without_biggest_value):
        """
        Returns the exception description.
        :param blm_interval:
        :param col_name:
        :param offset:
        :param offset_data_without_biggest_value:
        :return:
        """
        return '{} data stdev {:.0%} > {:.0%}:\n\tinterval: {}'.format(col_name, offset / np.average(offset_data_without_biggest_value), self.std_dev_threshold,
                                                                       blm_interval)

    def find_offset(self, offset_pandas_df, col_name, blm_interval):
        """
        Finds offset for a given blm_interval if possible.
        :param offset_pandas_df:
        :param col_name:
        :param blm_interval:
        :return:
        """
        if not offset_pandas_df.empty:
            offset_data = offset_pandas_df[col_name].values
            offset = np.average(offset_data)
            if not np.isnan(offset):
                if self.is_stdev_lower_than_threshold(offset_data, offset):
                    return offset
                else:
                    return self.remove_the_biggest_value_and_check_stdev(offset_data, blm_interval, col_name)
            else:
                raise self.OffsetNan('{} calculated offset is nan:\n\tinterval: {}'.format(col_name, blm_interval))
        else:
            raise self.OffsetEmpty('{} dataframe for offset calculation is empty:\n\tinterval: {}'.format(col_name, blm_interval))

    def remove_the_biggest_value_and_check_stdev(self, offset_data, blm_interval, col_name):
        """
        Removes the biggest value from data and checks if a new standard deviation is below the threshold. If no, it raises the exception.
        :param offset_data:
        :param blm_interval:
        :param col_name:
        :return:
        """
        offset_data_without_biggest_value = self.drop_the_biggest_abs_value(offset_data)
        offset = np.average(offset_data_without_biggest_value)
        if self.is_stdev_lower_than_threshold(offset_data_without_biggest_value, offset):
            return offset
        else:
            raise self.OffsetStdevOverThreshold(self.get_stdev_over_threshold_exception_description(blm_interval, col_name, offset, offset_data_without_biggest_value))


from abc import abstractmethod, abstractproperty

from source.Calculators.Calc import Calc
import numpy as np

class OffsetCalc(Calc):
    @property
    @abstractmethod
    def OffsetNan(self):
        pass

    @property
    @abstractmethod
    def OffsetEmpty(self):
        pass

    @property
    @abstractmethod
    def OffsetStdevOverThreshold(self):
        pass

    @property
    @abstractmethod
    def OffsetNotSetDueToNeighbourhood(self):
        pass

    @property
    @abstractmethod
    def blm_interval_offset_fields(self):
        return {'offset':None, 'offset_start':None, 'offset_end':None}

    @abstractmethod
    def get_blm_intervals_iterator(self, blm_intervals):
        pass

    @abstractmethod
    def get_offset_period(self, blm_intervals, col_name, data, current_blm_idx):
        pass

    def fill_interval_with_offset(self, blm_intervals, col_name, current_blm_idx, current_offset_val, data, offset_period_start, offset_period_end):
        try:
            offset_period = self.get_offset_period(blm_intervals, col_name, data, current_blm_idx)
            offset_data = data[offset_period]
            current_offset_val = self.find_offset(offset_data, col_name, blm_intervals[current_blm_idx])
            offset_period_start = offset_data.index[0]
            offset_period_end = offset_data.index[-1]
        except self.OffsetNotSetDueToNeighbourhood as e:
            e.logging_func('{}'.format(str(e)))
            pass
        except (self.OffsetNan, self.OffsetEmpty, self.OffsetNotSetDueToNeighbourhood) as e:
            e.logging_func('{}'.format(str(e)))
            pass
        finally:
            setattr(blm_intervals[current_blm_idx], self.blm_interval_offset_fields['offset'], current_offset_val)
            setattr(blm_intervals[current_blm_idx], self.blm_interval_offset_fields['offset_start'], offset_period_start)
            setattr(blm_intervals[current_blm_idx], self.blm_interval_offset_fields['offset_end'], offset_period_end)
            blm_intervals[current_blm_idx].should_plot = True
            return current_offset_val, offset_period_start, offset_period_end

    def run(self, data, blm_intervals):
        col_name = data.columns[0]
        current_offset_val = 0
        offset_period_start = data.index[0]
        offset_period_end = data.index[0]
        for current_blm_idx in self.get_blm_intervals_iterator(blm_intervals):
            current_offset_val, offset_period_start, offset_period_end = self.fill_interval_with_offset(blm_intervals, col_name, current_blm_idx,
                                                                                                            current_offset_val, data, offset_period_start,
                                                                                                            offset_period_end)

    def is_stdev_lower_than_threshold(self, data, average):
        return np.std(data) / average < self.std_dev_threshold

    def drop_the_biggest_abs_value(self, data):
        max_index = np.argmax(np.abs(data), axis=0)
        return np.concatenate((data[:max_index], data[max_index+1:]))

    def get_stdev_over_threshold_exception_description(self, blm_interval, col_name, offset, offset_data_without_biggest_value):
        return '{} data stdev {:.0%} > {:.0%}:\n\tinterval: {}'.format(col_name, offset / np.average(offset_data_without_biggest_value), self.std_dev_threshold,
                                                                       blm_interval)

    def find_offset(self, offset_pandas_df, col_name, blm_interval):
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
        offset_data_without_biggest_value = self.drop_the_biggest_abs_value(offset_data)
        offset = np.average(offset_data_without_biggest_value)
        if self.is_stdev_lower_than_threshold(offset_data_without_biggest_value, offset):
            return offset
        else:
            raise self.OffsetStdevOverThreshold(self.get_stdev_over_threshold_exception_description(blm_interval, col_name, offset, offset_data_without_biggest_value))


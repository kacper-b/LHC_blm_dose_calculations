from source.BLM_dose_calculation_exceptions import PreOffsetNan, PreOffsetEmpty, PreOffsetNotSetDueToNeighbourhood, PreOffsetStdevOverThreshold
from source.Calculators.Offset.OffsetCalc import OffsetCalc

class PreOffsetCalc(OffsetCalc):
    """
    The class implements pre-offset calculations. For every BLM interval it tries to calculate pre offset and assignees it.
    See the get_offset_period's method description for further details.
    """
    OffsetNan = PreOffsetNan
    OffsetEmpty = PreOffsetEmpty
    OffsetStdevOverThreshold = PreOffsetStdevOverThreshold
    OffsetNotSetDueToNeighbourhood = PreOffsetNotSetDueToNeighbourhood
    blm_interval_offset_fields = {'offset': 'offset_pre', 'offset_start': 'offset_pre_start', 'offset_end': 'offset_pre_end'}


    def get_blm_intervals_iterator(self, blm_intervals):
        """
        See the base's method description. The implementation returns BLM intervals' indices in the time ascending order.
        :param blm_intervals: BLM intervals
        :return:
        """
        return range(len(blm_intervals))

    def get_offset_period(self, blm_intervals, col_name, data, current_blm_interval_idx):
        """
        Finds and returns bool mask for a given data. True values are assignees to datapoints which should be used to pre-offset calculation.
        How it works?
        1. Try to take the data before the interval's beginning (range: [interval_beginning_timestamp - offset_length, interval_beginning_timestamp) )
        2. Check if the range is covered by the BLM data and if it doesn't overlap the data when the beam was on
        3. If the check result is True  -> return the mask with values within the range marked as True
        4. If the check result is False -> Try to take the data after the interval's end
         (range: (interval_end_timestamp + post_offset_shift, interval_end_timestamp + post_offset_shift + offset_length ] )
        5. Check if the range after the interval is covered by the BLM data and if it doesn't overlap the data when the beam was on
        6. If the check result is True  -> return the mask with values within the range (after the interval) marked as True
        7. If the check result is False -> raise exception OffsetNotSetDueToNeighbourhood. It implies that the old offset
            (if possible from one of the previous intervals) is assigned.

        :param col_name: dataframe column name == BLM name
        :param data: a BLM data
        :param current_blm_interval_idx: the current BLM interval's index
        :return:
        """
        # START: definitions of variables
        interval_start = blm_intervals[current_blm_interval_idx].start
        interval_end = blm_intervals[current_blm_interval_idx].end

        post_offset_period_start = interval_end + self.post_offset_shift
        post_offset_period_end = post_offset_period_start + self.offset_length

        pre_offset_period_start = interval_start - self.offset_length
        pre_offset_period_end = interval_start

        available_data_start = data.index[0]

        is_the_first_interval = current_blm_interval_idx == 0
        is_enough_data_before = available_data_start < pre_offset_period_start
        is_enough_space_between_prev_interval = (not is_the_first_interval and blm_intervals[current_blm_interval_idx-1].end < pre_offset_period_start) or is_the_first_interval
        # END: definitions of variables


        # checks if there is enough data available before the interval
        if is_enough_data_before and is_enough_space_between_prev_interval:
            return (pre_offset_period_start <= data.index) & (data.index < pre_offset_period_end)

        # if there is not enough data available before the interval, declares few extra variables
        available_data_end = data.index[-1]
        next_blm_idx = current_blm_interval_idx + 1
        is_interval_after_current = next_blm_idx < len(blm_intervals)
        is_enough_data_after = post_offset_period_end < available_data_end
        is_enough_space_between_next_interval = (is_interval_after_current and post_offset_period_end < blm_intervals[next_blm_idx].start) or not is_interval_after_current

        # checks if there is enough data available after the interval
        if is_enough_data_after and is_enough_space_between_next_interval:
            return (post_offset_period_start < data.index) & (data.index <= post_offset_period_end)
        else:
            # Keep an old offset
            raise self.OffsetNotSetDueToNeighbourhood('{} PreOffset neighbourhood is too small:\n\tinterval: {}'.format(col_name, blm_intervals[current_blm_interval_idx]))


if __name__  == '__main__':
    PreOffsetCalc(None, None, None)
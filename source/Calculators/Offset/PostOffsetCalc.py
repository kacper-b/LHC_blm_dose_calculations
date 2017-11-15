from source.BLM_dose_calculation_exceptions import PostOffsetNan, PostOffsetEmpty, PostOffsetNotSetDueToNeighbourhood, PostOffsetStdevOverThreshold
from source.Calculators.Offset.OffsetCalc import OffsetCalc

class PostOffsetCalc(OffsetCalc):
    """

    """
    OffsetNan = PostOffsetNan
    OffsetEmpty = PostOffsetEmpty
    OffsetStdevOverThreshold = PostOffsetStdevOverThreshold
    OffsetNotSetDueToNeighbourhood = PostOffsetNotSetDueToNeighbourhood
    blm_interval_offset_fields = {'offset': 'offset_post', 'offset_start': 'offset_post_start', 'offset_end': 'offset_post_end'}

    def __init__(self, offset_length=5 * 60, post_offset_shift=85, std_dev_threshold=0.5):
        """

        :param offset_length:
        :param post_offset_shift:
        :param std_dev_threshold:
        """
        super(PostOffsetCalc, self).__init__()
        self.offset_length = offset_length
        self.post_offset_shift = post_offset_shift
        self.std_dev_threshold = std_dev_threshold


    def get_blm_intervals_iterator(self, blm_intervals):
        """

        :param blm_intervals:
        :return:
        """
        return range(len(blm_intervals)-1,-1, -1)

    def get_offset_period(self, blm_intervals, col_name, data, current_blm_interval_idx):
        """

        :param blm_intervals:
        :param col_name:
        :param data:
        :param current_blm_interval_idx:
        :return:
        """
        # START: definitions of variables
        interval_start = blm_intervals[current_blm_interval_idx].start
        interval_end = blm_intervals[current_blm_interval_idx].end

        post_offset_period_start = interval_end + self.post_offset_shift
        post_offset_period_end = post_offset_period_start + self.offset_length

        pre_offset_period_start = interval_start - self.offset_length
        pre_offset_period_end = interval_start

        available_data_end = data.index[-1]
        next_blm_idx = current_blm_interval_idx + 1

        is_enough_data_after = post_offset_period_end < available_data_end
        is_it_the_first_interval = current_blm_interval_idx == 0
        is_interval_after_current = next_blm_idx < len(blm_intervals)
        is_enough_space_between_next_interval = (is_interval_after_current and post_offset_period_end < blm_intervals[next_blm_idx].start) or not is_interval_after_current
        is_enough_data_before = None
        is_enough_space_between_prev_interval = None
        # END: definitions of variables

        # if the interval beginning is too close to the beginning of data or to a previous interval check if there is enough space after the interval
        if not (is_enough_data_after and is_enough_space_between_next_interval):
            available_data_start = data.index[0]
            previous_blm_idx = current_blm_interval_idx - 1

            is_enough_data_before = available_data_start <= pre_offset_period_start
            is_enough_space_between_prev_interval = is_it_the_first_interval or blm_intervals[previous_blm_idx].end <= pre_offset_period_start

        if is_enough_data_after and is_enough_space_between_next_interval:
            return (post_offset_period_start < data.index) & (data.index <= post_offset_period_end)

        elif is_enough_data_before and is_enough_space_between_prev_interval:
            return (pre_offset_period_start <= data.index) & (data.index < pre_offset_period_end)

        else:
            raise self.OffsetNotSetDueToNeighbourhood('{} PostOffset neighbourhood is too small: {}'.format(col_name, blm_intervals[current_blm_interval_idx]))


if __name__  == '__main__':
    pass
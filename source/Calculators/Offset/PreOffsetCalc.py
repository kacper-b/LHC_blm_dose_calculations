from source.BLM_dose_calculation_exceptions import PreOffsetNan, PreOffsetEmpty, PreOffsetNotSetDueToNeighbourhood, PreOffsetStdevOverThreshold
from source.Calculators.Offset.OffsetCalc import OffsetCalc

class PreOffsetCalc(OffsetCalc):
    OffsetNan = PreOffsetNan
    OffsetEmpty = PreOffsetEmpty
    OffsetStdevOverThreshold = PreOffsetStdevOverThreshold
    OffsetNotSetDueToNeighbourhood = PreOffsetNotSetDueToNeighbourhood
    blm_interval_offset_fields = {'offset': 'offset_pre', 'offset_start': 'offset_pre_start', 'offset_end': 'offset_pre_end'}

    def __init__(self, offset_length=5 * 60, post_offset_shift=85, std_dev_threshold=0.5):
        super(PreOffsetCalc, self).__init__()
        self.offset_length = offset_length
        self.post_offset_shift = post_offset_shift
        self.std_dev_threshold = std_dev_threshold

    def get_blm_intervals_iterator(self, blm_intervals):
        return range(len(blm_intervals))

    def get_offset_period(self, blm_intervals, col_name, data, current_blm_idx):
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

        available_data_start = data.index[0]

        is_the_first_interval = current_blm_idx == 0
        is_enough_data_before = available_data_start < pre_offset_period_start
        is_enough_space_between_prev_interval = (not is_the_first_interval and blm_intervals[current_blm_idx-1].end < pre_offset_period_start) or is_the_first_interval
        is_enough_data_after = None
        is_enough_space_between_next_interval = None
        # END: definitions of variables

        # if the interval beginning is too close to the beginning of data or to a previous interval check if there is enough space after the interval
        if not (is_enough_data_before and is_enough_space_between_prev_interval):
            available_data_end = data.index[-1]
            next_blm_idx = current_blm_idx + 1
            is_interval_after_current = next_blm_idx < len(blm_intervals)
            is_enough_data_after = post_offset_period_end < available_data_end
            is_enough_space_between_next_interval = (is_interval_after_current and post_offset_period_end < blm_intervals[next_blm_idx].start) or not is_interval_after_current

        if is_enough_data_before and is_enough_space_between_prev_interval:
            return (pre_offset_period_start <= data.index) & (data.index < pre_offset_period_end)

        elif is_enough_data_after and is_enough_space_between_next_interval:
            return (post_offset_period_start < data.index) & (data.index <= post_offset_period_end)

        else:
            raise self.OffsetNotSetDueToNeighbourhood('{} PreOffset neighbourhood is too small:\n\tinterval: {}'.format(col_name, blm_intervals[current_blm_idx]))


if __name__  == '__main__':
    pass
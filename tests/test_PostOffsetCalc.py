from unittest.mock import MagicMock
import numpy as np
import pandas as pd
from source.Calculators.Offset.PostOffsetCalc import PostOffsetCalc

not_enough_space_before_because_of_data_enough_after = MagicMock(start=0.5, end=2.5, offset_post=None, offset_post_expected=35.5)
enough_space_before = MagicMock(start=4.6, end=5.6, offset_post=None, offset_post_expected=35.5)
nan_before_not_enough_after = MagicMock(start=7.5, end=9.5, offset_post=None, offset_post_expected=157.0)
not_enough_space_before_not_enough_after_because_of_intervals = MagicMock(start=9.6, end=10, offset_post=None, offset_post_expected=157.0)
not_enough_space_before_because_of_interval_not_enough_between_next_interval = MagicMock(start=10.5, end=11.5, offset_post=None, offset_post_expected=157.0)
not_enough_space_before_because_of_interval_enough_data_after = MagicMock(start=13.6, end=14.5, offset_post=None, offset_post_expected=157.0)

blm_intervals =[not_enough_space_before_because_of_data_enough_after,
                enough_space_before,
                nan_before_not_enough_after,
                not_enough_space_before_not_enough_after_because_of_intervals,
                not_enough_space_before_because_of_interval_not_enough_between_next_interval,
                not_enough_space_before_because_of_interval_enough_data_after]

t = np.arange(0, 17, 0.1)
blm_data = t*10
blm_data[7] = np.nan
data = pd.DataFrame(data={'intensity': blm_data}, index=t)
post_offset_calc = PostOffsetCalc(2, 0.2)

def __reset_offsets():
    for blm_int_mock in blm_intervals:
        blm_int_mock.offset_post = None


def test_PostOffset_shouldUsePostOffset_ifPostOffsetPeriodIsTooSmall():
    __reset_offsets()
    post_offset_calc.run(data, blm_intervals)
    assert blm_intervals[0].offset_post == blm_intervals[0].offset_post_expected


def test_PostOffset_shouldUsePreOffset_ifPostOffsetPeriodIsBigEnough():
    __reset_offsets()
    post_offset_calc.run(data, blm_intervals)
    assert blm_intervals[1].offset_post == blm_intervals[1].offset_post_expected


def test_PostOffset_shouldUsePostOffset_ifPostOffsetIsNanAndPreOffsetPeriodIsTooSmallBecauseOfNextInterval():
    __reset_offsets()
    post_offset_calc.run(data, blm_intervals)
    assert blm_intervals[2].offset_post == blm_intervals[2].offset_post_expected


def test_PostOffset_shouldKeepOldOffset_ifPostAndPreOffsetPeriodsAreTooSmall():
    __reset_offsets()
    post_offset_calc.run(data, blm_intervals)
    assert blm_intervals[3].offset_post == blm_intervals[3].offset_post_expected


def test_PostOffset_shouldUsePostOffset_ifPostOffsetPeriodIsTooSmallAndPreIsOk():
    __reset_offsets()
    post_offset_calc.run(data, blm_intervals)
    assert blm_intervals[4].offset_post == blm_intervals[4].offset_post_expected


def test_PostOffset_shouldKeepOldOffset_ifPostOffsetPeriodIsLimitedByPreviousIntervalAndPreOffsetPeriodIsTooSmall():
    __reset_offsets()
    post_offset_calc.run(data, blm_intervals)
    assert blm_intervals[5].offset_post == blm_intervals[5].offset_post_expected
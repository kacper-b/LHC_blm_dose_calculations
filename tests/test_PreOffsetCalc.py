from unittest.mock import MagicMock
import numpy as np
import pandas as pd
from source.Calculators.Offset.PreOffsetCalc import PreOffsetCalc

not_enough_space_before_enough_after = MagicMock(start=0.5, end=2.5, offset_pre=None, offset_pre_expected=36.5)
enough_space_before = MagicMock(start=4.7, end=5.5, offset_pre=None, offset_pre_expected=36.5)
nan_before_not_enough_after = MagicMock(start=7.5, end=9.5, offset_pre=None, offset_pre_expected=36.5)
not_enough_space_before_not_enough_after_because_of_intervals = MagicMock(start=9.6, end=10, offset_pre=None, offset_pre_expected=36.5)
not_enough_space_before_because_of_interval_enough_after = MagicMock(start=10.5, end=11.4, offset_pre=None, offset_pre_expected=125.5)
not_enough_space_before_not_enough_after = MagicMock(start=13.6, end=14.5, offset_pre=None, offset_pre_expected=125.5)

blm_intervals =[not_enough_space_before_enough_after,
                enough_space_before,
                nan_before_not_enough_after,
                not_enough_space_before_not_enough_after_because_of_intervals,
                not_enough_space_before_because_of_interval_enough_after,
                not_enough_space_before_not_enough_after]

t = np.arange(0, 16.,0.1)
blm_data = t*10
blm_data[7] = np.nan
data = pd.DataFrame(data={'intensity':blm_data}, index=t)
pre_offset_calc = PreOffsetCalc(2, 0.2)

def __reset_offsets():
    for blm_int_mock in blm_intervals:
        blm_int_mock.offset_pre = None

def test_PreOffset_shouldUsePostOffset_ifPreOffsetPeriodIsTooSmall():
    __reset_offsets()
    pre_offset_calc.run(data, blm_intervals)
    assert blm_intervals[0].offset_pre == blm_intervals[0].offset_pre_expected

def test_PreOffset_shouldUsePreOffset_ifPreOffsetPeriodIsBigEnough():
    __reset_offsets()
    pre_offset_calc.run(data, blm_intervals)
    assert blm_intervals[1].offset_pre == blm_intervals[1].offset_pre_expected

def test_PreOffset_shouldUsePostOffset_ifPreOffsetIsNanAndPostOffsetPeriodIsTooSmallBecauseOfNextInterval():
    __reset_offsets()
    pre_offset_calc.run(data, blm_intervals)
    assert blm_intervals[2].offset_pre == blm_intervals[2].offset_pre_expected

def test_PreOffset_shouldKeepOldOffset_ifPreAndPostOffsetPeriodsAreTooSmall():
    __reset_offsets()
    pre_offset_calc.run(data, blm_intervals)
    assert blm_intervals[3].offset_pre == blm_intervals[3].offset_pre_expected

def test_PreOffset_shouldUsePostOffset_ifPreOffsetPeriodIsTooSmallAndPostIsOk():
    __reset_offsets()
    pre_offset_calc.run(data, blm_intervals)
    assert blm_intervals[4].offset_pre == blm_intervals[4].offset_pre_expected

def test_PreOffset_shouldKeepOldOffset_ifPreOffsetPeriodIsLimitedByPreviousIntervalAndPostOffsetPeriodIsTooSmall():
    __reset_offsets()
    pre_offset_calc.run(data, blm_intervals)
    assert blm_intervals[5].offset_pre == blm_intervals[5].offset_pre_expected
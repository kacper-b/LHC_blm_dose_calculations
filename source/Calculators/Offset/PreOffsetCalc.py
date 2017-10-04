import numpy as np

from source.BLM_dose_calculation_exceptions import PreOffsetNan, PreOffsetEmpty
from source.Calculators.Offset.OffsetCalc import OffsetCalc


class PreOffsetCalc(OffsetCalc):
    def __init__(self, offset_sec=5 * 60):
        self.offset_sec = offset_sec

    def run(self, data, blm_intervals):
        col_name = data.columns[0]
        offset = 0
        for blm_interval in blm_intervals:
            try:
                offset = self.__find_offset(data, col_name, blm_interval)
            except (PreOffsetNan, PreOffsetEmpty) as e:
                pass
            finally:
                blm_interval.offset_pre = offset

    def __find_offset(self, data, col_name, blm_interval):
        offset_period = (data.index >= (blm_interval.start - self.offset_sec)) & (data.index <= blm_interval.start)
        offset_interval_pre = data[offset_period]

        if not offset_interval_pre.empty:
            offset = np.mean(offset_interval_pre[col_name])
            if not np.isnan(offset):
                return offset
            else:
                raise PreOffsetNan('{} pre-offset dataframe is empty: {}'.format(col_name, blm_interval))
        else:
            raise PreOffsetEmpty('{} pre-offset dataframe is empty: {}'.format(col_name, blm_interval))

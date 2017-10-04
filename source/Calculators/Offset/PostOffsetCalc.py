import numpy as np

from source.BLM_dose_calculation_exceptions import PostOffsetNan, PostOffsetEmpty
from source.Calculators.Offset.OffsetCalc import OffsetCalc


class PostOffsetCalc(OffsetCalc):
    def __init__(self, offset_sec=5 * 60):
        self.offset_sec = offset_sec

    def run(self, data, blm_intervals):
        col_name = data.columns[0]
        offset = 0
        for blm_interval in blm_intervals:
            try:
                new_offset = self.__find_offset(data, col_name, blm_interval)
            except (PostOffsetNan, PostOffsetEmpty) as e:
                pass
            else:
                offset = new_offset
            finally:
                blm_interval.offset_post = offset

    def __find_offset(self, data, col_name, blm_interval):
        offset_period = (data.index >= blm_interval.end) & (data.index <= blm_interval.end + self.offset_sec)
        offset_interval_post = data[offset_period]

        if not offset_interval_post.empty:
            offset = np.mean(offset_interval_post[col_name])
            if not np.isnan(offset):
                return offset
            else:
                raise PostOffsetNan('Post-offset value is Nan: {} {}'.format(col_name, blm_interval))
        else:
            raise PostOffsetEmpty('Post-offset dataframe is empty: {} {}'.format(col_name, blm_interval))

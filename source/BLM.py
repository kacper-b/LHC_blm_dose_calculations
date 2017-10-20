import re
from source.BLMInterval import BLMInterval
import _pickle as pickle
import os
from source.BLM_dose_calculation_exceptions import BLMIntervalsEmpty, BLMDataEmpty
from sortedcontainers import SortedSet


class BLM:
    regex_name_pattern = re.compile(r"([\w\.\-]+):(\w+)")
    date_format = '%Y_%m_%d'

    def __init__(self, name, data, position=None):
        self.name = name
        self.position = position
        self.data = data
        self.blm_intervals = None

    def create_blm_intervals(self, intensity_intervals):
        self.blm_intervals = SortedSet(BLMInterval(ii.start, ii.end, ii.integrated_intensity_offset_corrected) for ii in intensity_intervals)
        return self.blm_intervals

    def get_missing_blm_intervals(self, intervals_set_container_to_check):
        if self.blm_intervals is not None:
            return intervals_set_container_to_check - self.blm_intervals

    def set(self, calc):
        if self.blm_intervals is not None and not self.data.empty:
            calc.run(self.data, self.blm_intervals)
        else:
            if self.blm_intervals is None:
                raise BLMIntervalsEmpty('No valid {} intervals'.format(self.name))
            else:
                raise BLMDataEmpty('No data for {}'.format(self.name))

    def get_post_oc_dose(self, start=None, end=None):
        return self.__get_dose(lambda blm: blm.integral_post_offset_corrected, start, end)

    def get_oc_intensity_integral(self, start=None, end=None):
        return self.__get_dose(lambda blm: blm.integrated_intensity_offset_corrected, start, end)

    def get_pre_oc_dose(self, start=None, end=None):
        return self.__get_dose(lambda blm: blm.integral_pre_offset_corrected, start, end)

    def get_raw_dose(self, start=None, end=None):
        return self.__get_dose(lambda blm: blm.integral_raw, start, end)

    def get_file_name(self, start, end):
        name_field = re.match(BLM.regex_name_pattern, self.name)
        if name_field:
            name = name_field.group(1).replace('.', '_')
            field = name_field.group(2)
            start = start.strftime(BLM.date_format)
            end = end.strftime(BLM.date_format)
            return '{0}_{1}_{2}_{3}'.format(name, start, end, field)

    def to_pickle(self, directory, start, end):
        self.clean_blm_intervals_from_temporary_data()
        with open(os.path.join(directory, self.get_file_name(start, end)) + '.p', 'wb') as f:
            pickle.dump(self, f)

    def clean_blm_intervals_from_temporary_data(self, clean_blm_data=False):
        for blm_i in self.blm_intervals:
            blm_i.clean_data()
        if clean_blm_data:
            self.data = None

    def __get_dose(self, func, start, end):
        if not start or not end:
            return sum(func(blm_int) for blm_int in self.blm_intervals)
        else:
            start_in_sec = start.timestamp()
            end_in_sec = end.timestamp()
            return sum(func(blm_int) for blm_int in self.blm_intervals
                       if self.__is_interval_between_dates(blm_int, start_in_sec, end_in_sec))

    def __is_interval_between_dates(self, blm_interval, start, end):
        return start <= blm_interval.start and blm_interval.end <= end

    def __sort_blm_intervals_by_starting_date(self, blm_intervals):
        return sorted(blm_intervals, key=(lambda blm_interval: blm_interval.start))

    def __str__(self):
        if self.blm_intervals is not None:
            return self.name + '\n' + '\n'.join(map(str, self.blm_intervals))

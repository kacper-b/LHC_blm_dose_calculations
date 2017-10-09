import re
from _datetime import datetime
import pickle
import os


class BLM:
    regex_name_pattern = re.compile(r"([\w\.]+):(\w+)")
    date_format = '%Y_%m_%d'

    def __init__(self, name, data, position=None):
        self.name = name
        self.position = position
        self.data = data
        self.blm_intervals = None

    def create_blm_intervals(self, intensity_intervals):
        blm_intervals_gen = (BLMInterval(start=ii.start, end=ii.end) for ii in intensity_intervals)
        self.blm_intervals = self.__sort_blm_intervals_by_starting_date(blm_intervals_gen)

    def set(self, calc):
        if self.blm_intervals is not None:
            calc.run(self.data, self.blm_intervals)

    def get_post_oc_dose(self, start=None, end=None):
        return self.__get_dose(lambda blm: blm.integral_post_offset_corrected, start, end)

    def get_pre_oc_dose(self, start=None, end=None):
        return self.__get_dose(lambda blm: blm.integral_pre_offset_corrected, start, end)

    def get_raw_dose(self, start=None, end=None):
        return self.__get_dose(lambda blm: blm.integral_raw, start, end)

    def get_file_name(self):
        name_field = re.match(BLM.regex_name_pattern, self.name)
        if name_field and self.blm_intervals:
            name = name_field.group(1).replace('.', '_')
            field = name_field.group(2)
            start = datetime.utcfromtimestamp(self.blm_intervals[0].start).strftime(BLM.date_format)
            end = datetime.utcfromtimestamp(self.blm_intervals[-1].end).strftime(BLM.date_format)
            return '{0}_{1}_{2}_{3}'.format(name, start, end, field)

    def to_pickle(self, directory):
        with open(os.path.join(directory, self.get_file_name()) + '.p', 'wb') as f:
            pickle.dump(self, f)

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


class BLMInterval:
    date_str_format = '%Y-%m-%d %X'

    def __init__(self, start=None, end=None):
        self.start = start
        self.end = end
        self.offset_pre = 0
        self.offset_pre_start = None
        self.offset_pre_end = None
        self.offset_post = 0
        self.offset_post_start = None
        self.offset_post_end = None
        self.integral_raw = 0
        self.integral_pre_offset_corrected = 0
        self.integral_post_offset_corrected = 0
        self.should_plot = None

    def get_integrated_data(self, data):
        if self.start is not None and self.end is not None:
            return data[(self.start <= data.index) & (data.index <= self.end)]

    def get_preoffset_data(self, data):
        if self.offset_pre_start is not None and self.offset_pre_end is not None:
            return data[(self.offset_pre_start <= data.index) & (data.index <= self.offset_pre_end)]

    def get_postoffset_data(self, data):
        if self.offset_pre_start is not None and self.offset_pre_end is not None:
            return data[(self.offset_post_start <= data.index) & (data.index <= self.offset_post_end)]

    def __str__(self):
        return 'start: {}\tend: {}\tPre-offset: {:3.1e}\tPost-offset: {:3.1e}\traw integral: {}\tintegral_pre_oc: {}\tintegral_post_oc: {}'. \
            format(datetime.utcfromtimestamp(self.start).strftime(BLMInterval.date_str_format),
                   datetime.utcfromtimestamp(self.end).strftime(BLMInterval.date_str_format),
                   self.offset_pre, self.offset_post, self.integral_raw, self.integral_pre_offset_corrected, self.integral_post_offset_corrected)

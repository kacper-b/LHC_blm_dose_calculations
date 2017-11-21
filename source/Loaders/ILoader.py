from abc import ABC, abstractmethod
from datetime import timedelta
import glob
import os

import logging


class ILoader(ABC):
    def __init__(self, file_regex_pattern, date_format):
        self.regex = file_regex_pattern
        self.file_paths = []
        self.data = []
        self.date_format = date_format
        self.dt = timedelta(milliseconds=1)

    def set_files_paths(self, directory, start, end, field):
        """

        :param directory:
        :param start:
        :param end:
        :param field:
        :return:
        """
        file_paths = list(filename for filename in glob.iglob(os.path.join(directory, '*')) if self.is_file_name_valid(filename, start, end, field))
        self.file_paths.extend(file_path for file_path in file_paths)
        logging.info('{}\n\t{}'.format(self.__class__.__name__,'\n\t'.join(self.file_paths)))

    def clean(self):
        self.file_paths = []
        self.data = []

    def is_file_dates_cover_analysed_time_period(self, period_start, period_end, file_date_start, file_date_end):
        dt = self.dt
        result = (period_start < file_date_end - self.dt) and (file_date_start + self.dt < period_end)
        is_between = (period_start - dt <= file_date_start) and (file_date_end <= period_end + dt)
        is_end_covers = file_date_start < period_end < file_date_end + dt
        is_beginning_covers = file_date_start - dt < period_start < file_date_end
        if (is_between or is_end_covers or is_beginning_covers) != result:
            raise Exception('TEST: DATESS!')
        return result


    @abstractmethod
    def load_pickles(self):
        pass

    @abstractmethod
    def is_file_name_valid(self, filename, start, end, field):
        pass
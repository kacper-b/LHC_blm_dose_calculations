from abc import ABC, abstractmethod
from datetime import timedelta
import glob
import os

import logging


class ILoader(ABC):
    """
    That abstract class provides common functionality that is used during files loading.
    """
    def __init__(self, file_regex_pattern, date_format):
        """
        :param str file_regex_pattern: a regular expression which is used during file_names parsing
        :param date_format:
        """
        self.regex = file_regex_pattern
        self.file_paths = []
        self.data = []
        self.date_format = date_format
        self.dt = timedelta(milliseconds=1)

    def set_files_paths(self, directory, start, end, field):
        """
        It sets pickles' file paths. It considers only files which data's range overlaps [start, end]
        :param str directory: directory with pickle files
        :param datetime start: the analyzed period's beginning
        :param datetime end: the analyzed period's end
        :param str field: the analyzed field (ex. LOSS_RS12)
        :return:
        """
        file_paths = list(filename for filename in glob.iglob(os.path.join(directory, '*')) if self.is_file_name_valid(filename, start, end, field))
        self.file_paths.extend(file_paths)
        logging.info('{}\n\t{}'.format(self.__class__.__name__,'\n\t'.join(self.file_paths)))

    def clean(self):
        """
        It cleans stored file_paths and loaded data.
        :return:
        """
        self.file_paths = []
        self.data = []

    def is_file_dates_cover_analysed_time_period(self, period_start, period_end, file_date_start, file_date_end):
        """
        It checks if file's dates overlaps an analysed period.
        :param datetime period_start:
        :param datetime period_end:
        :param datetime file_date_start:
        :param datetime file_date_end:
        :return: True if file's dates overlaps an analysed period
        """
        return (period_start < file_date_end - self.dt) and (file_date_start + self.dt < period_end)


    @abstractmethod
    def load_pickles(self):
        """
         Abstract method - an implementation should iterate over pickle files (their paths are assigned to the file_paths list) and load them.
         :return:
         """
        pass

    @abstractmethod
    def is_file_name_valid(self, filename, start, end, field):
        """
        Abstract method - an implementation should checks if a file path belongs to a file which should be loaded. It compares: BLM name, time range and field name.
        :param file_path: path to a file
        :param datetime start: the required data's end timestamp
        :param datetime end: the required data's end timestamp
        :param str field: a part of Timber's variable name, which appears after ":" (ex. LOSS_RS12)
        :return bool: logical value which tells if the file should be loaded
        """
        pass
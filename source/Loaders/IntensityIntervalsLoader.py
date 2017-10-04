import glob
import os
import pickle
import re
import sys
from datetime import datetime, timedelta

from config import INTENSITY_INTERVALS_FILES_REGEX_PATTERN


class IntensityIntervalsLoader:
    """

    """

    def __init__(self, file_regex_pattern=INTENSITY_INTERVALS_FILES_REGEX_PATTERN):
        """

        :param file_regex_pattern:
        """
        self.regex = file_regex_pattern
        self.file_paths = []
        self.intensity_intervals = []

    def set_files_paths(self, directory, start, end):
        """

        :param directory:
        :param start:
        :param end:
        :return:
        """
        append_to_self_paths = self.file_paths.append
        dt = timedelta(milliseconds=1)
        for filename in glob.iglob(os.path.join(directory, '**/*'), recursive=True):
            start_end_date = re.match(self.regex, filename)
            if start_end_date:
                start_file_date = datetime.strptime(start_end_date.group(1), '%Y%m%d')
                end_file_date = datetime.strptime(start_end_date.group(2), '%Y%m%d')
                is_between = (start - dt <= start_file_date and end_file_date <= end + dt)
                is_end_covers = start_file_date < end < end_file_date + dt
                is_beginning_covers = start_file_date - dt < start < end_file_date
                if is_between or is_end_covers or is_beginning_covers:
                    append_to_self_paths(filename)

    def read_pickled_intensity_intervals(self):
        """

        :return:
        """
        import projects.LHC_intensity_calculations.source
        sys.modules['source'] = projects.LHC_intensity_calculations.source
        extenend_intensity_intervals = self.intensity_intervals.extend
        for file_path in self.file_paths:
            with open(file_path, 'rb') as interval_pickle:
                extenend_intensity_intervals(pickle.load(interval_pickle))

    def filter_interval_by_dates(self, start_date, end_date):
        """

        :param start_date:
        :param end_date:
        :return:
        """
        start_in_sec = (start_date - datetime.utcfromtimestamp(0)).total_seconds()
        end_in_sec = (end_date - datetime.utcfromtimestamp(0)).total_seconds()
        func = (lambda interval: start_in_sec <= interval.start and interval.end <= end_in_sec)
        self.intensity_intervals = list(filter(func, self.intensity_intervals))

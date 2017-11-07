import pickle
import re
import sys
from datetime import datetime

from config import INTENSITY_INTERVALS_FILES_REGEX_PATTERN, INTENSITY_INTERVALS_DATE_FORMAT
from source.Loaders.ILoader import ILoader


class IntensityIntervalsLoader(ILoader):
    """

    """

    def __init__(self):
        super(IntensityIntervalsLoader, self).__init__(INTENSITY_INTERVALS_FILES_REGEX_PATTERN, INTENSITY_INTERVALS_DATE_FORMAT)

    def set_files_paths(self, directory, start, end):
        super(IntensityIntervalsLoader, self).set_files_paths(directory, start, end, None)

    def is_file_name_valid(self, filename, start, end, field):
        start_end_date = re.match(self.regex, filename)
        dt = self.dt
        if start_end_date:
            start_file_date = datetime.strptime(start_end_date.group(1), self.date_format)
            end_file_date = datetime.strptime(start_end_date.group(2), self.date_format)
            is_between = (start - dt <= start_file_date and end_file_date <= end + dt)
            is_end_covers = start_file_date < end < end_file_date + dt
            is_beginning_covers = start_file_date - dt < start < end_file_date
            if (is_between or is_end_covers or is_beginning_covers) != self.is_file_dates_cover_analysed_time_period(start, end, start_file_date,
                                                                                                                     end_file_date):
                raise Exception('DATESS! int')
            if is_between or is_end_covers or is_beginning_covers:
                return True
        return False

    def filter_interval_by_dates(self, start_date, end_date):
        """

        :param start_date:
        :param end_date:
        :return:
        """
        start_in_sec = (start_date - datetime.utcfromtimestamp(0)).total_seconds()
        end_in_sec = (end_date - datetime.utcfromtimestamp(0)).total_seconds()
        func = (lambda interval: start_in_sec <= interval.start and interval.end <= end_in_sec)
        self.data = list(filter(func, self.data))

    def filter_interval_by_valid_flag(self):
        """

        :param start_date:
        :param end_date:
        :return:
        """
        func = (lambda interval: interval.isValid())
        self.data = list(filter(func, self.data))

    def load_pickles(self):
        import projects.LHC_intensity_calculations.source
        sys.modules['source'] = projects.LHC_intensity_calculations.source
        extenend_intensity_intervals = self.data.extend
        for file_path in self.file_paths:
            with open(file_path, 'rb') as interval_pickle:
                extenend_intensity_intervals(pickle.load(interval_pickle))


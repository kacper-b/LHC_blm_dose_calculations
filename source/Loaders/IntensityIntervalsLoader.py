import pickle
import re
import sys
from datetime import datetime
import config
from tools.workers import str2datetime
from config import INTENSITY_INTERVALS_FILES_REGEX_PATTERN, INTENSITY_INTERVALS_DATE_FORMAT
from source.Loaders.ILoader import ILoader


class IntensityIntervalsLoader(ILoader):
    """
    The classes allows to load a pickled intensity intervals.
    """
    def __init__(self):
        super(IntensityIntervalsLoader, self).__init__(INTENSITY_INTERVALS_FILES_REGEX_PATTERN, INTENSITY_INTERVALS_DATE_FORMAT)

    def set_files_paths(self, directory, start, end, field=None):
        """
        It sets intensity pickles' file paths. It considers only files which data's range overlaps [start, end]
        :param str directory: a directory with pickled intensity intervals
        :param datetime start: the analyzed period's beginning
        :param datetime end: the analyzed period's end
        :param str field: doesn't used for intensity files
        :return:
        """
        super(IntensityIntervalsLoader, self).set_files_paths(directory, start, end, None)

    def is_file_name_valid(self, filename, start, end, field):
        """
         It checks if a file with a given path should be loaded. It compares: BLM name, time range and field name.
         :param file_path: path to a file
         :param datetime start: the required data's end timestamp
         :param datetime end: the required data's end timestamp
         :param str field: doesn't used for intensity files
         :return bool: logical value which tells if the file should be loaded
         """
        regex_match = re.match(self.regex, filename)
        if regex_match:
            start_file_date = str2datetime(regex_match.group(1), self.date_format)
            end_file_date = str2datetime(regex_match.group(2), self.date_format)
            return self.is_file_dates_cover_analysed_time_period(start, end, start_file_date, end_file_date)
        return False

    def filter_interval_by_dates(self, runs):
        """
        It removes intensity intervals which are outside required time range.
        :param datetime start_date:
        :param datetime end_date:
        :return:
        """
        epoch_time = datetime.utcfromtimestamp(0)
        runs_in_sec = [((start_date - epoch_time).total_seconds(), (end_date - epoch_time).total_seconds()) for start_date, end_date in runs]
        # start_in_sec = (start_date - epoch_time).total_seconds()
        # end_in_sec = (end_date - epoch_time).total_seconds()
        func = (lambda interval: any(start_in_sec <= interval.start and interval.end <= end_in_sec for start_in_sec, end_in_sec, in runs_in_sec))
        self.data = list(filter(func, self.data))

    def filter_interval_by_valid_flag(self):
        """
        It removes intensity intervals which are marked as invalid.
        :return:
        """
        func = (lambda interval: interval.isValid())
        self.data = list(filter(func, self.data))

    def load_pickles(self):
        """
        It iterates over pickle files (their paths are assigned to the file_paths list) and load them to data field.
        :return:
        """
        # In order to import pickled classes the implementation has to be known.
        import projects.LHC_intensity_calculations.source
        sys.modules['source'] = projects.LHC_intensity_calculations.source

        extenend_intensity_intervals = self.data.extend
        for file_path in self.file_paths:
            with open(file_path, 'rb') as interval_pickle:
                extenend_intensity_intervals(pickle.load(interval_pickle))


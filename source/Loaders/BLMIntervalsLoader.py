import glob
import os
import pickle
import re
from datetime import datetime, timedelta

import pandas as pd

from config import BLM_FILES_REGEX_PATTERN, BLM_DATE_FORMAT
from source.BLM import BLM
from source.BLM_dose_calculation_exceptions import BLMLoaderWrongNumberOfColumns

class BLMIntervalsLoader:
    """

    """

    def __init__(self, names=[], file_regex_pattern=BLM_FILES_REGEX_PATTERN):
        """

        """
        self.names = [name.replace('.', '_') for name in names]
        self.regex = file_regex_pattern
        self.file_paths = []

    def set_files_path(self, directory, start, end, field):
        """

        :param directory:
        :param start:
        :param end:
        :param field:
        :return:
        """

        file_paths = (filename for filename in glob.iglob(os.path.join(directory, '*')) if self.is__file_name_valid(filename, start, end, field))
        self.file_paths = [file_path for file_path in file_paths]

    def is__file_name_valid(self, filename, start, end, field):
        """

        :param filename:
        :param start:
        :param end:
        :param field:
        :return:
        """
        start_end_date = re.match(self.regex, filename)
        if start_end_date:
            blm_name = start_end_date.group(1)
            start_file_date = datetime.strptime(start_end_date.group(2), BLM_DATE_FORMAT)
            end_file_date = datetime.strptime(start_end_date.group(3), BLM_DATE_FORMAT)
            field_in_file = start_end_date.group(4)
            is_field_right = field == field_in_file
            is_blm_right = blm_name in self.names
            dt = timedelta(milliseconds=5)
            is_between = (start_file_date - dt <= start and end <= end_file_date + dt)
            if not (is_blm_right and is_field_right):
                return False
            return is_between
        return False

    def load_blm(self):
        for file_path in self.file_paths:
            with open(file_path, 'rb') as blm_pickle:
                return pickle.load(blm_pickle)

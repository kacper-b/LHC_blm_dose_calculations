import pandas as pd
import os
import re
import pickle
from datetime import datetime, timedelta
from config import BLM_FILES_REGEX_PATTERN, BLM_DATE_FORMAT
from BLM_dose_calculation_exceptions import BLMLoaderWrongNumberOfColumns
from BLMDoseCalc import BLMDoseCalc
import glob


class BLMsLoader:
    """

    """
    def __init__(self, names=[], file_regex_pattern=BLM_FILES_REGEX_PATTERN):
        """

        """
        self.names = [name.replace('.','_') for name in names]
        self.regex = file_regex_pattern
        self.file_paths = []
        self.blm_data = []

    def set_files_path(self, directory, start, end, field):
        """

        :param directory:
        :param start:
        :param end:
        :param field:
        :return:
        """
        file_paths = (filename for filename in glob.iglob(os.path.join(directory,'**/*'), recursive=True)
                      if self.is_file_name_valid(filename, start, end, field))
        self.file_paths = [file_path for file_path in file_paths]

    def is_file_name_valid(self, filename, start, end, field):
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
            if not (is_blm_right and is_field_right):
                return False
            dt = timedelta(milliseconds=1)
            is_between = (start - dt <= start_file_date and end_file_date <= end + dt)
            is_end_covers = start_file_date < end < end_file_date + dt
            is_beginning_covers = start_file_date - dt < start < end_file_date
            return is_between or is_end_covers or is_beginning_covers
        return False

    def read_pickled_blms(self):
        """

        :return:
        """
        for file_path in self.file_paths:
            with open(file_path, 'rb') as blm_pickle:
                self.blm_data.append(pickle.load(blm_pickle))

    def group_by_blm_name(self):
        """

        :return:
        """
        if any(map(lambda blm: len(blm.columns)!=1, self.blm_data)):
            raise BLMLoaderWrongNumberOfColumns('Data from BLM should have only one column!')

        blm_name_data_dict = {}
        for blm in self.blm_data:
            blm_name_data_dict[blm.columns[0]] = blm_name_data_dict.setdefault(blm.columns[0], pd.DataFrame()).append(blm)
        for blm in blm_name_data_dict.values():
            blm.sort_index(inplace=True)
        return blm_name_data_dict

    def get_blms(self):
        return (BLMDoseCalc(key, data) for key,data in self.group_by_blm_name().items())


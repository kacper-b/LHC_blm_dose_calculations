from source.Loaders.IBLMsLoader import IBLMsLoader
import os
import pickle
import re
from datetime import datetime
import pandas as pd
from config import BLM_DATE_FORMAT
from source.BLM import BLM
from source.BLM_dose_calculation_exceptions import BLMLoaderWrongNumberOfColumns


class BLMsRawPandasDataLoader(IBLMsLoader):
    def __init__(self, names=[]):
        super(BLMsRawPandasDataLoader, self).__init__(names)

    def is__file_name_valid(self, file_path, start, end, field):
        dt = self.dt
        start_end_date = re.match(self.regex, file_path)
        if start_end_date:
            blm_name = start_end_date.group(1)
            start_file_date = datetime.strptime(start_end_date.group(2), BLM_DATE_FORMAT)
            end_file_date = datetime.strptime(start_end_date.group(3), BLM_DATE_FORMAT)
            field_in_file = start_end_date.group(4)
            is_field_right = field == field_in_file
            is_blm_right = blm_name in self.names
            if not (is_blm_right and is_field_right):
                return False
            is_between = (start - dt <= start_file_date and end_file_date <= end + dt)
            is_end_covers = start_file_date < end < end_file_date + dt
            is_beginning_covers = start_file_date - dt < start < end_file_date
            return is_between or is_end_covers or is_beginning_covers
        return False

    def set_files_paths(self, directory, start, end, field):
        for blm_name in self.names:
            super(IBLMsLoader, self).set_files_paths(os.path.join(directory, blm_name), start, end, field)

    def load_pickles(self):
        for file_path in self.file_paths:
            with open(file_path, 'rb') as blm_pickle:
                self.data.append(pickle.load(blm_pickle))

    def group_by_blm_name(self):
        """

        :return:
        """
        if any(map(lambda blm: len(blm.columns) != 1, self.data)):
            raise BLMLoaderWrongNumberOfColumns('Data from BLM should have only one column!')

        blm_name_data_dict = {}
        for blm in self.data:
            blm_name_data_dict[blm.columns[0]] = blm_name_data_dict.setdefault(blm.columns[0], pd.DataFrame()).append(blm)
        for blm in blm_name_data_dict.values():
            blm.sort_index(inplace=True)
        return blm_name_data_dict

    def get_blms(self):
        return (BLM(key, data) for key, data in self.group_by_blm_name().items())


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

    def is_file_name_valid(self, file_path, start, end, field):
        dt = self.dt
        regex_match = re.match(self.regex, file_path)
        if regex_match:
            blm_name, end_file_date, field_in_file, start_file_date = self.extract_blm_dates_fied_from_filename(regex_match)
            is_field_right = field == field_in_file
            is_blm_right = blm_name in self.names
            if not (is_blm_right and is_field_right):
                return False
            is_between = (start - dt <= start_file_date and end_file_date <= end + dt)
            is_end_covers = start_file_date < end < end_file_date + dt
            is_beginning_covers = start_file_date - dt < start < end_file_date
            if (is_between or is_end_covers or is_beginning_covers) != self.is_file_dates_cover_analysed_time_period(start, end, start_file_date,
                                                                                                                     end_file_date):
                print('between{} end{} beg{} oliv{} start{} end{} fname_st{} fname_end{}'.format(is_between, is_end_covers, is_beginning_covers, self.is_file_dates_cover_analysed_time_period(start, end, start_file_date,
                                                                                                                     end_file_date), start, end, start_file_date, end_file_date))
                raise Exception('DATESS! blm raw')
            return is_between or is_end_covers or is_beginning_covers
        return False

    def set_files_paths(self, directory, start, end, field):
        for blm_name in self.names:
            super(IBLMsLoader, self).set_files_paths(os.path.join(directory, blm_name), start, end, field)

    def load_pickles(self):
        for file_path in self.file_paths:
            with open(file_path, 'rb') as blm_pickle:
                data = pickle.load(blm_pickle)
                self.data.append(data)

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
            blm.dropna(axis=0, how='any', inplace=True)
            # blm.fillna(method='pad', inplace=True)
            # blm.fillna(method='bfill', inplace=True)
        return blm_name_data_dict

    def get_blms(self):
        return (BLM(key, data) for key, data in self.group_by_blm_name().items())


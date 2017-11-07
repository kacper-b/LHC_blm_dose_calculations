from source.Loaders.IBLMsLoader import IBLMsLoader
import pickle
import re
from datetime import datetime
from config import BLM_DATE_FORMAT


class BLMsCalculatedLoader(IBLMsLoader):
    def __init__(self, names, remove_raw_data=False):
        super(BLMsCalculatedLoader, self).__init__(names)
        self.remove_raw_data = remove_raw_data

    def is_file_name_valid(self, filename, start, end, field):
        """

        :param filename:
        :param start:
        :param end:
        :param field:
        :return:
        """
        dt = self.dt
        regex_match = re.match(self.regex, filename)
        if regex_match:
            blm_name, end_file_date, field_in_file, start_file_date = self.extract_blm_dates_fied_from_filename(regex_match)

            is_field_right = field == field_in_file
            is_blm_right = blm_name in self.names

            if not (is_blm_right and is_field_right):
                return False
            is_between = (start - dt <= start_file_date and end_file_date <= end + dt)
            is_end_covers = start_file_date < end < end_file_date + dt
            is_beginning_covers = start_file_date - dt < start < end_file_date
            if (is_between or is_end_covers or is_beginning_covers) != self.is_file_dates_cover_analysed_time_period(start, end, start_file_date, end_file_date):
                raise Exception('DATESS! calculat')
            return is_between or is_end_covers or is_beginning_covers
        return False

    def extract_blm_dates_fied_from_filename(self, start_end_date):
        blm_name = start_end_date.group(1)
        start_file_date = datetime.strptime(start_end_date.group(2), BLM_DATE_FORMAT)
        end_file_date = datetime.strptime(start_end_date.group(3), BLM_DATE_FORMAT)
        field_in_file = start_end_date.group(4)
        return blm_name, end_file_date, field_in_file, start_file_date

    def load_pickles(self):
        blm = None
        for file_path in self.file_paths:
            with open(file_path, 'rb') as blm_pickle:
                blm_loaded = pickle.load(blm_pickle)
                if self.remove_raw_data:
                    blm_loaded.data = None

                if blm is None:
                    blm = blm_loaded
                elif blm.name == blm_loaded.name:
                    blm.blm_intervals.update(blm_loaded.blm_intervals)
                else:
                    raise Exception('something went wrong: BLMs with different names ')
        return blm

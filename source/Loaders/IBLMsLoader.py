import re
from datetime import datetime

from config import BLM_FILES_REGEX_PATTERN, BLM_DATE_FORMAT
from source.Loaders.ILoader import ILoader


class IBLMsLoader(ILoader):
    """
    That abstract class provides common functionality that is used during stored pickles BLM data loading.
    """
    def __init__(self, names):
        """
        It initializes an object with BLM names.
        :param names: BLM names
        """
        super(IBLMsLoader, self).__init__(BLM_FILES_REGEX_PATTERN, BLM_DATE_FORMAT)
        self.names = [name.replace('.', '_') for name in names]

    def extract_blmname_dates_filed_from_filename(self, start_end_date):
        """
        It unpacks re.match result and converts it to a tuple.
        :param re.match start_end_date: a result of the re.match function which consists:
            blm_name, start_file_date, end_file_date, field_in_file (ex. LOSS_RS12) in groups
        :return tuple:  blm_name, start_file_date, end_file_date, field_in_file
        """
        blm_name = start_end_date.group(1)
        start_file_date = datetime.strptime(start_end_date.group(2), BLM_DATE_FORMAT)
        end_file_date = datetime.strptime(start_end_date.group(3), BLM_DATE_FORMAT)
        field_in_file = start_end_date.group(4)
        return blm_name, end_file_date, field_in_file, start_file_date

    def is_file_name_valid(self, file_path, start, end, field):
        """
        It checks if a file path belongs to a file which should be loaded. It compares: BLM name, time range and field name.
        :param file_path: path to a file
        :param datetime start: the required data's end timestamp
        :param datetime end: the required data's end timestamp
        :param str field: a part of Timber's variable name, which appears after ":" (ex. LOSS_RS12)
        :return bool: logical value which tells if the file should be loaded
        """
        regex_match = re.match(self.regex, file_path)
        if regex_match:
            blm_name, end_file_date, field_in_file, start_file_date = self.extract_blmname_dates_filed_from_filename(regex_match)
            is_field_right = field == field_in_file
            is_blm_right = blm_name in self.names
            return is_blm_right and is_field_right and self.is_file_dates_cover_analysed_time_period(start, end, start_file_date, end_file_date)
        return False


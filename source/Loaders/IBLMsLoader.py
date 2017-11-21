import re
from datetime import datetime

from config import BLM_FILES_REGEX_PATTERN, BLM_DATE_FORMAT
from source.Loaders.ILoader import ILoader


class IBLMsLoader(ILoader):
    def __init__(self, names):
        super(IBLMsLoader, self).__init__(BLM_FILES_REGEX_PATTERN, BLM_DATE_FORMAT)
        self.names = [name.replace('.', '_') for name in names]

    def extract_blmname_dates_filed_from_filename(self, start_end_date):
        blm_name = start_end_date.group(1)
        start_file_date = datetime.strptime(start_end_date.group(2), BLM_DATE_FORMAT)
        end_file_date = datetime.strptime(start_end_date.group(3), BLM_DATE_FORMAT)
        field_in_file = start_end_date.group(4)
        return blm_name, end_file_date, field_in_file, start_file_date

    def is_file_name_valid(self, file_path, start, end, field):
        regex_match = re.match(self.regex, file_path)
        if regex_match:
            blm_name, end_file_date, field_in_file, start_file_date = self.extract_blmname_dates_filed_from_filename(regex_match)
            is_field_right = field == field_in_file
            is_blm_right = blm_name in self.names
            return is_blm_right and is_field_right and self.is_file_dates_cover_analysed_time_period(start, end, start_file_date, end_file_date)
        return False


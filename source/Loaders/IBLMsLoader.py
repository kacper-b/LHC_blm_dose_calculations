from datetime import datetime

from config import BLM_FILES_REGEX_PATTERN, BLM_DATE_FORMAT
from source.Loaders.ILoader import ILoader


class IBLMsLoader(ILoader):
    def __init__(self, names):
        super(IBLMsLoader, self).__init__(BLM_FILES_REGEX_PATTERN, BLM_DATE_FORMAT)
        self.names = [name.replace('.', '_') for name in names]

    def extract_blm_dates_fied_from_filename(self, start_end_date):
        blm_name = start_end_date.group(1)
        start_file_date = datetime.strptime(start_end_date.group(2), BLM_DATE_FORMAT)
        end_file_date = datetime.strptime(start_end_date.group(3), BLM_DATE_FORMAT)
        field_in_file = start_end_date.group(4)
        return blm_name, end_file_date, field_in_file, start_file_date

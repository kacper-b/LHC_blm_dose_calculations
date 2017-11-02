from config import BLM_FILES_REGEX_PATTERN, BLM_DATE_FORMAT
from source.Loaders.ILoader import ILoader


class IBLMsLoader(ILoader):
    def __init__(self, names):
        super(IBLMsLoader, self).__init__(BLM_FILES_REGEX_PATTERN, BLM_DATE_FORMAT)
        self.names = [name.replace('.', '_') for name in names]

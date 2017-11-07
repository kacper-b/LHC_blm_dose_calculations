from source.Loaders.IBLMsLoader import IBLMsLoader
import pickle
import re
from datetime import datetime
from config import BLM_DATE_FORMAT


class BLMsCalculatedLoader(IBLMsLoader):
    def __init__(self, names, remove_raw_data=False):
        super(BLMsCalculatedLoader, self).__init__(names)
        self.remove_raw_data = remove_raw_data

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

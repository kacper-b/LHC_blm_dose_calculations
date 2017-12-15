from source.Loaders.IBLMsLoader import IBLMsLoader
import pickle
import re
from datetime import datetime
from config import BLM_DATE_FORMAT


class BLMsCalculatedLoader(IBLMsLoader):
    """
    The classes allows to load already calculated BLMs (BLM intervals) from pickle files.
    """
    def __init__(self, names, remove_raw_data=False):
        """
        Initializes the object with names of BLMs which should be loaded.
        :param names: BLMs' names
        :param remove_raw_data: if set to True, a raw BLM data will be removed from loaded pickles.
        """
        super(BLMsCalculatedLoader, self).__init__(names)
        self.remove_raw_data = remove_raw_data

    def load_pickles(self):
        """
        Iterates over pickle files (their paths are assigned to the file_paths list)
        :return: Loaded BLM
        """
        blm = None
        for file_path in self.file_paths:
            with open(file_path, 'rb') as blm_pickle:
                blm_loaded = pickle.load(blm_pickle)
                if self.remove_raw_data:
                    blm_loaded.data = None

                # if that is the first iteration of the for loop assign the loaded BLM to the BLM which will be returned
                if blm is None:
                    blm = blm_loaded
                # if two pickles for the same BLM exists merge their BLM intervals
                elif blm.name == blm_loaded.name:
                    blm.blm_intervals.update(blm_loaded.blm_intervals)
                else:
                    # TODO: change to specific exception
                    raise Exception('something went wrong: BLMs with different names ')
        return blm

from source.Loaders.IBLMsLoader import IBLMsLoader
import os
import pickle
import pandas as pd
from source.BLM import BLM
from source.BLM_dose_calculation_exceptions import BLMLoaderWrongNumberOfColumns


class BLMsRawPandasDataLoader(IBLMsLoader):
    """
    The classes allows to load a raw BLM data stored as pickled pandas dataframes.
    """
    def __init__(self, names=[]):
        super(BLMsRawPandasDataLoader, self).__init__(names)

    def set_files_paths(self, directory, start, end, field):
        """
        It sets BLM pickles' file paths. It considers only files which data's range overlaps [start, end]
        :param str directory: a parent directory for all BLMs' directories (with raw data)
        :param datetime start: the analyzed period's beginning
        :param datetime end: the analyzed period's end
        :param str field: the analyzed field (ex. LOSS_RS12)
        :return:
        """
        for blm_name in self.names:
            super(IBLMsLoader, self).set_files_paths(os.path.join(directory, blm_name), start, end, field)

    def load_pickles(self):
        """
         It iterates over pickle files (their paths are assigned to the file_paths list)
         :return:
         """
        for file_path in self.file_paths:
            with open(file_path, 'rb') as blm_pickle:
                data = pickle.load(blm_pickle)
                self.data.append(data)

    def _group_by_blm_name(self):
        """
        It merges loaded pickles into the dict.
        :return dict: the dict has format: { blm_name1: pandas_dataframe_with_all_data_for_blm1, blm_name2:pandas_dataframe_with_all_data_for_blm2}
        """
        if any(map(lambda blm: len(blm.columns) != 1, self.data)):
            raise BLMLoaderWrongNumberOfColumns('Data from BLM should have only one column!')

        # It merges loaded pickles into a one dict { blm_name: pandas_dataframe_with_all_data_for_that_blm, }
        blm_name_data_dict = {}
        for blm in self.data:
            blm_name_data_dict[blm.columns[0]] = blm_name_data_dict.setdefault(blm.columns[0], pd.DataFrame()).append(blm)

        # Sorts and removes nan values from the data
        for blm in blm_name_data_dict.values():
            blm.sort_index(inplace=True)
            blm.dropna(axis=0, how='any', inplace=True)
        return blm_name_data_dict

    def get_blms(self):
        """
        It provides BLM class objects (without assigned position in the LHC).
        :return generator: BLM generator which provides BLM class objects filled with data
        """
        return (BLM(key, data) for key, data in self._group_by_blm_name().items())


from source.Loaders.IBLMsLoader import IBLMsLoader
import os
import pickle
import pandas as pd
from source.BLM import BLM
from source.BLM_dose_calculation_exceptions import BLMLoaderWrongNumberOfColumns


class BLMsRawPandasDataLoader(IBLMsLoader):
    def __init__(self, names=[]):
        super(BLMsRawPandasDataLoader, self).__init__(names)

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
        return blm_name_data_dict

    def get_blms(self):
        return (BLM(key, data) for key, data in self.group_by_blm_name().items())


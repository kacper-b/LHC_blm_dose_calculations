import os

import numpy as np
import pandas as pd

from config import DATA_DIRs_NAMES


class DosesCalculationReader:
    """

    """

    def __init__(self, integrated_dose_column_name='TOTAL'):
        """

        :param integrated_dose_column_name:
        """
        self.df = None
        self.dose_col_name = integrated_dose_column_name

    def read_csv(self, file_path=os.path.join(DATA_DIRs_NAMES['blm_lists'], 'blm_data_2016_nn_new.csv')):
        """

        :param file_path:
        :return:
        """
        self.df = pd.read_csv(file_path, index_col=0).sort_values(self.dose_col_name)

    def get_blms(self, num=None):
        """

        :param num:
        :return:
        """
        if num:
            indices = np.linspace(0, len(self.df[self.dose_col_name]) - 1, num=num, dtype=int)
        else:
            indices = range(len(self.df[self.dose_col_name]))
        return (self.df.iloc[idx].name for idx in indices)

    def save_to_file(self, file_path, blm_names):
        with open(file_path, 'w') as f:
            f.write('\n'.join('{},{}\n'.format(blm_name, self.df.loc[blm_name][self.dose_col_name])
                              for blm_name in blm_names))


if __name__ == '__main__':
    file_path = os.path.join(DATA_DIRs_NAMES['blm_lists'], 'blm_data_2016_nn_new.csv')

    dcr = DosesCalculationReader()

    dcr.read_csv(file_path)
    results_csv = os.path.join(DATA_DIRs_NAMES['blm_lists'], 'test_blms.csv')

    dcr.save_to_file(results_csv, dcr.get_blms(10))

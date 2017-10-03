import os
import time
from datetime import datetime
from statsmodels.nonparametric.smoothers_lowess import lowess
from DosesCalculationReader import DosesCalculationReader
from config import DATA_DIRs_NAMES, PICKLE_INTENSITY_INTERVALS_PATH
from multiprocessing import Pool
from IntensityIntervalsLoader import IntensityIntervalsLoader
from BLMsLoader import BLMsLoader


def run(blm):
    return blm.name, sum(map(blm.integrate_over_intensity_interval, iil.intensity_intervals))


if __name__ == '__main__':
    st = (time.time())
    iil = IntensityIntervalsLoader()
    start = datetime(year=2016, month=4, day=4)
    end = datetime(year=2016, month=12, day=5)
    field = 'LOSS_RS12'

    iil.set_files_paths(PICKLE_INTENSITY_INTERVALS_PATH, start, end)
    iil.read_pickled_intensity_intervals()
    iil.filter_interval_by_dates(start, end)

    # dcr = DosesCalculationReader()
    # file_path = os.path.join(DATA_DIRs_NAMES['blm_lists'], 'blm_data_2016_nn_new.csv')
    # dcr.read_csv(file_path)
    # blm_names = list(dcr.get_blms())
    blm_names = ['BLMTI.04L5.B2E10_TANC.4L5',
                 'BLMTI.04R5.B1E10_TANC.4R5',
                 'BLMQI.32R2.B2E30_MQ',
                 'BLMQI.19L1.B2E30_MQ',
                 'BLMQI.16L8.B1E30_MQ',
                 'BLMQI.13R8.B2E30_MQ',
                 'BLMEI.04R6.B2I10_MSDA.C4R6.B2']

    blm_loader = BLMsLoader(blm_names)

    blm_loader.set_files_path('/media/sf_monitoring_analysis/data/blm_data', start, end, field)
    blm_loader.read_pickled_blms()
    blms = list(blm_loader.get_blms())

    print(time.time()-st)
    N = 1

    pool = Pool(processes=N)

    results = pool.map(run, blms)
    # results = map(run, blms)
    for blm_name, dose in results:
        print(blm_name, dose)

    print(time.time()-st)


import time
from datetime import datetime
from multiprocessing import Pool
import os
from config import PICKLE_INTENSITY_INTERVALS_DIR
from source.Calculators.Integral.PostOffsetCorrectedIntegralCalc import PostOffsetCorrectedIntegralCalc
from source.Calculators.Integral.PreOffsetCorrectedIntegralCalc import PreOffsetCorrectedIntegralCalc
from source.Calculators.Integral.RawIntegralCalc import RawIntegralCalc
from source.Calculators.Offset.PostOffsetCalc import PostOffsetCalc
from source.Calculators.Offset.PreOffsetCalc import PreOffsetCalc
from source.Loaders.BLMsDataLoader import BLMsDataLoader
from source.Loaders.IntensityIntervalsLoader import IntensityIntervalsLoader
from projects.Timber_downloader.source.BLM_classes.BLMsParser import BLMsParser
# import cProfile
from source.BLM_dose_calculation_exceptions import BLMDataEmpty, BLMIntervalsEmpty
from source.Calculators.PlotCalc import PlotCalc
from config import BLM_INTERVALS_PLOTS_DIR, PICKLE_BLM_INTERVALS_DIR, BLM_DATA_DIR, BLM_LIST_DIR


calculators = [PreOffsetCalc(), PostOffsetCalc(), RawIntegralCalc(),
               PostOffsetCorrectedIntegralCalc(), PreOffsetCorrectedIntegralCalc(),
               # PlotCalc(BLM_INTERVALS_PLOTS_DIR)
               ]


def set_blm_calculators(blm):
    for calc in calculators:
        blm.set(calc)


def run(blm):
    try:
        blm.create_blm_intervals(iil.intensity_intervals)
        set_blm_calculators(blm)
        # cProfile.runctx('set_blm_calculators(blm)', globals(), locals(), 'profile-%s.out' % blm.get_file_name())
        blm.to_pickle(PICKLE_BLM_INTERVALS_DIR)
        result = blm.name, blm.get_pre_oc_dose(), blm.get_post_oc_dose(),  blm.get_raw_dose()
        print('DONE:\t', blm.name)
        return result
    except (BLMDataEmpty, BLMIntervalsEmpty) as e:
        print(e)


# def fill_blms_with_intensity_intervals(blms, intensity_intervals):
#     for blm in blms:
#         blm.create_blm_intervals(intensity_intervals)


if __name__ == '__main__':
    st = (time.time())
    iil = IntensityIntervalsLoader()
    start = datetime(year=2016, month=4, day=4)
    end = datetime(year=2016, month=12, day=6)
    field = 'LOSS_RS12'

    iil.set_files_paths(PICKLE_INTENSITY_INTERVALS_DIR, start, end)
    iil.read_pickled_intensity_intervals()
    iil.filter_interval_by_dates(start, end)

    blm_names = (blm.raw_name for blm in BLMsParser.read(os.path.join(BLM_LIST_DIR, 'tcp_ir3_ir7.csv')))

    blm_loader = BLMsDataLoader(blm_names)

    blm_loader.set_files_path(BLM_DATA_DIR, start, end, field)
    blm_loader.read_pickled_blms()
    blms = list(blm_loader.get_blms())

    middle = time.time()
    print(middle - st)

    N = 8
    pool = Pool(processes=N)
    blms = pool.map(run, blms)

    for blm in blms:
        print(blm)
    print(time.time() - middle)

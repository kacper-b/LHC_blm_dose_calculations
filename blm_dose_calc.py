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
from source.Calculators.PlotCalc import PlotCalc
from source.Calculators.SmoothingCalc import SmoothingCalc
from config import BLM_INTERVALS_PLOTS_DIR, PICKLE_BLM_INTERVALS_DIR, BLM_DATA_DIR, BLM_LIST_DIR


def run(blm):
    pre_offset_calc = PreOffsetCalc()
    post_offset_calc = PostOffsetCalc()
    raw_integral_calc = RawIntegralCalc()
    post_integral_calc = PostOffsetCorrectedIntegralCalc()
    pre_integral_calc = PreOffsetCorrectedIntegralCalc()
    plot_calc = PlotCalc(BLM_INTERVALS_PLOTS_DIR)
    smoothing_calc = SmoothingCalc()
    # blm.set(smoothing_calc)
    blm.set(pre_offset_calc)
    blm.set(post_offset_calc)
    blm.set(raw_integral_calc)
    blm.set(post_integral_calc)
    blm.set(pre_integral_calc)
    print(blm.name)
    # blm.set(plot_calc)
    blm.to_pickle(PICKLE_BLM_INTERVALS_DIR)
    return blm.name, blm.get_pre_oc_dose(), blm.get_post_oc_dose(),  blm.get_raw_dose()


def fill_blms_with_intensity_intervals(blms, intensity_intervals):
    for blm in blms:
        blm.create_blm_intervals(intensity_intervals)


if __name__ == '__main__':
    st = (time.time())
    iil = IntensityIntervalsLoader()
    start = datetime(year=2016, month=4, day=4)
    end = datetime(year=2016, month=12, day=6)
    field = 'LOSS_RS12'

    iil.set_files_paths(PICKLE_INTENSITY_INTERVALS_DIR, start, end)
    iil.read_pickled_intensity_intervals()
    iil.filter_interval_by_dates(start, end)

    blm_names = (blm.raw_name for blm in BLMsParser.read(os.path.join(BLM_LIST_DIR, 'test_blm_list.csv')))

    blm_loader = BLMsDataLoader(blm_names)

    blm_loader.set_files_path(BLM_DATA_DIR, start, end, field)
    blm_loader.read_pickled_blms()
    blms = list(blm_loader.get_blms())

    fill_blms_with_intensity_intervals(blms, iil.intensity_intervals)
    middle = time.time()
    print(middle - st)

    N = 8
    pool = Pool(processes=N)
    blms = pool.map(run, blms)

    for blm in blms:
        print(blm)
    print(time.time() - middle)

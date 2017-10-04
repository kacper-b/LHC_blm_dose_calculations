import time
from datetime import datetime
from multiprocessing import Pool

from config import PICKLE_INTENSITY_INTERVALS_PATH
from source.Calculators.Integral.PostOffsetCorrectedIntegralCalc import PostOffsetCorrectedIntegralCalc
from source.Calculators.Integral.PreOffsetCorrectedIntegralCalc import PreOffsetCorrectedIntegralCalc
from source.Calculators.Integral.RawIntegralCalc import RawIntegralCalc
from source.Calculators.Offset.PostOffsetCalc import PostOffsetCalc
from source.Calculators.Offset.PreOffsetCalc import PreOffsetCalc
from source.Loaders.BLMsDataLoader import BLMsDataLoader
from source.Loaders.IntensityIntervalsLoader import IntensityIntervalsLoader

pre_offset_calc = PreOffsetCalc()
post_offset_calc = PostOffsetCalc()
raw_integral_calc = RawIntegralCalc()
post_integral_calc = PostOffsetCorrectedIntegralCalc()
pre_integral_calc = PreOffsetCorrectedIntegralCalc()


def run(blm):
    blm.set(pre_offset_calc)
    blm.set(post_offset_calc)
    blm.set(raw_integral_calc)
    blm.set(pre_integral_calc)
    return blm.name, blm.get_oc_dose(), blm.get_raw_dose()


def fill_blms_with_intensity_intervals(blms, intensity_intervals):
    for blm in blms:
        blm.create_blm_intervals(intensity_intervals)


if __name__ == '__main__':
    st = (time.time())
    iil = IntensityIntervalsLoader()
    start = datetime(year=2016, month=4, day=4)
    end = datetime(year=2016, month=12, day=5)
    field = 'LOSS_RS12'

    iil.set_files_paths(PICKLE_INTENSITY_INTERVALS_PATH, start, end)
    iil.read_pickled_intensity_intervals()
    iil.filter_interval_by_dates(start, end)

    blm_names = ['BLMTI.04L5.B2E10_TANC.4L5',
                 'BLMTI.04R5.B1E10_TANC.4R5',
                 'BLMQI.32R2.B2E30_MQ',
                 'BLMQI.19L1.B2E30_MQ',
                 'BLMQI.16L8.B1E30_MQ',
                 'BLMQI.13R8.B2E30_MQ',
                 'BLMEI.04R6.B2I10_MSDA.C4R6.B2']

    blm_loader = BLMsDataLoader(blm_names)

    blm_loader.set_files_path('/media/sf_monitoring_analysis/data/blm_data', start, end, field)
    blm_loader.read_pickled_blms()
    blms = list(blm_loader.get_blms())

    fill_blms_with_intensity_intervals(blms, iil.intensity_intervals)
    middle = time.time()
    print(middle - st)

    N = 4
    pool = Pool(processes=N)
    blms = pool.map(run, blms)

    for blm in blms:
        print(blm)
    print(time.time() - middle)

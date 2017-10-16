import os
import time
from datetime import datetime
from multiprocessing import Pool
import config
from projects.Timber_downloader.source.BLM_classes.BLMsParser import BLMsParser
import warnings
from config import PICKLE_BLM_INTERVALS_DIR, BLM_DATA_DIR, BLM_LIST_DIR
from config import PICKLE_INTENSITY_INTERVALS_DIR, BLM_INTERVALS_PLOTS_DIR
from source.BLM_dose_calculation_exceptions import BLMDataEmpty, BLMIntervalsEmpty
from source.Calculators.Integral.PostOffsetCorrectedIntegralCalc import PostOffsetCorrectedIntegralCalc
from source.Calculators.Integral.PreOffsetCorrectedIntegralCalc import PreOffsetCorrectedIntegralCalc
from source.Calculators.Integral.RawIntegralCalc import RawIntegralCalc
from source.Calculators.Offset.PostOffsetCalc import PostOffsetCalc
from source.Calculators.Offset.PreOffsetCalc import PreOffsetCalc
from source.Loaders.BLMsDataLoader import BLMsDataLoader
from source.Loaders.IntensityIntervalsLoader import IntensityIntervalsLoader
from source.Plotters.BLMsPlotter import BLMsPlotter
from source.Plotters.PlotCalc import PlotCalc
from source.Loaders.BLMIntervalsLoader import BLMIntervalsLoader

calculators = [PreOffsetCalc(), PreOffsetCorrectedIntegralCalc(),
               RawIntegralCalc(),
               PostOffsetCalc(), PostOffsetCorrectedIntegralCalc(),
               # PlotCalc(BLM_INTERVALS_PLOTS_DIR)
               ]


def set_blm_calculators(blm):
    for calc in calculators:
        blm.set(calc)


def run(name_position):
    blm_name = name_position[0]
    blm_position = name_position[1]
    try:

        blm_names_list = [blm_name, ]
        print('start:\t', blm_name)

        blm_intervals_loader = BLMIntervalsLoader(blm_names_list)
        blm_intervals_loader.set_files_path(PICKLE_BLM_INTERVALS_DIR, start, end, field)

        if blm_intervals_loader.file_paths:
            print('exists:\t', blm_name)
            return blm_intervals_loader.load_blm()
        else:
            try:
                blm_loader = BLMsDataLoader(blm_names_list)
                blm_loader.set_files_path(BLM_DATA_DIR, start, end, field)
                blm_loader.read_pickled_blms()
                blm_list = list(blm_loader.get_blms())
                blm = blm_list[0]
                blm.position = blm_position

                blm.create_blm_intervals(iil.intensity_intervals)
                set_blm_calculators(blm)
                # blm.to_pickle(PICKLE_BLM_INTERVALS_DIR, start, end)
                print('DONE:\t', blm.name)
                # return blm
            except (BLMDataEmpty, BLMIntervalsEmpty) as e:
                print(e)
    except Exception as e:
        warnings.warn(blm_name + str(e))


if __name__ == '__main__':
    st = (time.time())
    iil = IntensityIntervalsLoader()
    start = datetime(year=2017, month=5, day=1)
    end = datetime(year=2017, month=9, day=20)
    field = 'LOSS_RS12'

    iil.set_files_paths(PICKLE_INTENSITY_INTERVALS_DIR, start, end)
    iil.read_pickled_intensity_intervals()
    iil.filter_interval_by_dates(start, end)

    blm_csv_content = {blm.raw_name: blm.position for blm in BLMsParser.read(os.path.join(BLM_LIST_DIR, 'corina5R5.csv'))}
    name_position_dict = blm_csv_content.items()
    N = 7
    pool = Pool(processes=N)
    blms = pool.map(run, name_position_dict)

    # for blm in blms:
    #     print(blm.name, blm.get_pre_oc_dose())
    #
    p = BLMsPlotter('.')
    #
    p.plot_normalized_dose(blms, lambda blm: blm.get_pre_oc_dose(), lambda blm: blm.get_oc_intensity_integral())

    # p.plot_oc_dose(blms2, )

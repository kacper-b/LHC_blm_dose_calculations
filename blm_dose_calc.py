import os
import time
import sys, traceback

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
from source.Loaders.BLMsRawPandasDataLoader import BLMsRawPandasDataLoader
from source.Loaders.IntensityIntervalsLoader import IntensityIntervalsLoader
from source.Plotters.BLMsPlotter import BLMsPlotter
from source.Plotters.PlotCalc import PlotCalc
from source.Loaders.BLMsCalculatedLoader import BLMsCalculatedLoader
from source.BLM import BLM
from source.BLMFactory import BLMFactory

calculators = [PreOffsetCalc(), PreOffsetCorrectedIntegralCalc(),
               RawIntegralCalc(),
               PostOffsetCalc(), PostOffsetCorrectedIntegralCalc(),
               # PlotCalc(BLM_INTERVALS_PLOTS_DIR)
               ]


def set_blm_calculators(blm):
    for calc in calculators:
        blm.set(calc)


def run(blm):
    print('start:\t', blm.name)

    try:
        blm_names_list = [blm.name, ]
        blm_loader = BLMsRawPandasDataLoader(blm_names_list)
        blm_loader.set_files_paths(BLM_DATA_DIR, start, end, field)
        blm_loader.load_pickles()
        blm_data = next(blm_loader.get_blms()).data
        blm.data = blm_data

        calculated_blms_loader = BLMsCalculatedLoader(blm_names_list)
        calculated_blms_loader.set_files_paths(PICKLE_BLM_INTERVALS_DIR, start, end, field)

        if calculated_blms_loader.file_paths:
            print('exists:\t', blm.name)
            blm_calculated = calculated_blms_loader.load_pickles()
            blm_calculated.data = None

            missing_intervals = blm.get_missing_blm_intervals(blm_calculated.blm_intervals)
            if not missing_intervals:
                print('not missing anything:\t', blm.name)
                return blm
            else:
                print('missing {}'.format(len(missing_intervals)))
                blm_already_caluclated_blms = blm.blm_intervals
                blm.blm_intervals = missing_intervals
                set_blm_calculators(blm)
                blm.blm_intervals = blm_already_caluclated_blms | blm.blm_intervals
        else:
            set_blm_calculators(blm)

        # blm.clean_blm_intervals_from_temporary_data(clean_blm_data=True)
        blm.name = blm.name + ':' + field
        blm.to_pickle(PICKLE_BLM_INTERVALS_DIR, start, end)
        print('DONE:\t', blm.name)
        return blm
    except (BLMDataEmpty, BLMIntervalsEmpty) as e:
        print(e)


if __name__ == '__main__':
    st = (time.time())
    iil = IntensityIntervalsLoader()
    start = datetime(year=2015, month=7, day=25)
    end = datetime(year=2015, month=11, day=15)
    field = 'LOSS_RS12'

    iil.set_files_paths(PICKLE_INTENSITY_INTERVALS_DIR, start, end)
    iil.load_pickles()
    iil.filter_interval_by_dates(start, end)

    blm_csv_content = {blm.raw_name: blm.position for blm in BLMsParser.read(os.path.join(BLM_LIST_DIR, 'corina5R1.csv'))}

    factory = BLMFactory()
    N = 4
    with Pool(processes=N) as pool:
        blms = pool.map(run, factory.build(iil.data, blm_csv_content))



    p = BLMsPlotter('.')

    z = p.plot_normalized_dose(blms, lambda blm: blm.get_pre_oc_dose(), lambda blm: blm.get_oc_intensity_integral())
    for i in range(len(z[0])):
        print(z[0][i],z[1][i])
    # p.plot_pre_oc_dose(blms, lambda blm: blm.get_pre_oc_dose())
    #
    #

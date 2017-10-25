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
from source.BLMProcess import BLMProcess
import logging
logging.basicConfig(level=logging.CRITICAL)

if __name__ == '__main__':
    number_of_simultaneous_processes = 1
    calculators = [PreOffsetCalc(), PreOffsetCorrectedIntegralCalc(),
                   RawIntegralCalc(),
                   PostOffsetCalc(), PostOffsetCorrectedIntegralCalc(),
                   # PlotCalc(BLM_INTERVALS_PLOTS_DIR)
                   ]
    start = datetime(year=2016, month=5, day=10)
    end = datetime(year=2016, month=6, day=17)
    field = 'LOSS_RS12'
    blm_list_file_path = os.path.join(BLM_LIST_DIR, 'corina5R5B2.scv')

    iil = IntensityIntervalsLoader()
    iil.set_files_paths(PICKLE_INTENSITY_INTERVALS_DIR, start, end)
    iil.load_pickles()
    iil.filter_interval_by_dates(start, end)

    blm_csv_content = {blm.raw_name: blm.position for blm in BLMsParser.read(blm_list_file_path)}
    factory = BLMFactory()
    blm_process = BLMProcess(start, end, field, calculators, should_return_blm=True)

    with Pool(processes=number_of_simultaneous_processes) as pool:
        blms = pool.map(blm_process.run, factory.build(iil.data, blm_csv_content))

    for blm in blms:
        print(blm.name, blm.get_pre_oc_dose())

    p = BLMsPlotter('.')
    # p.plot_total_dose(blms, lambda blm: blm.get_pre_oc_dose())
    z = p.plot_normalized_dose(blms, lambda blm: blm.get_pre_oc_dose(), lambda blm: blm.get_oc_intensity_integral())


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
import pandas as pd
from config import IPs, LHC_LENGTH


logging.basicConfig(level=logging.WARNING)

def get_IP_position(IP_num):
    df_ips = pd.DataFrame(IPs, columns=['dcum', 'ipn', 'ip', 'pos'])
    df_ips.index = df_ips['dcum']

    return df_ips[df_ips['ipn'] == IP_num]['dcum'].values[0]

def is_blm_in_ip_neighbourhood(blm, ip_num, left_offset=700, right_offset=700):
    ip_position = get_IP_position(ip_num)
    interval_start = ip_position - left_offset
    interval_end = ip_position + right_offset
    lhc_len = LHC_LENGTH
    blm.position = blm.position / 100 #convert cm to m
    if blm.position < 0:
        blm.position+=lhc_len
    if interval_end <= lhc_len and interval_start >=0 and interval_start < blm.position < interval_end:
        return True
    elif interval_end <= lhc_len and interval_start < 0 and blm.position >= (lhc_len + interval_start):
        blm.position -= lhc_len
        return True
    elif interval_end <= lhc_len and interval_start < 0 and interval_end >= blm.position >= 0:
        return True
    return False

def is_blm_in_arc_after_ip(blm, ip_num, left_offset=700, right_offset=700):
    ip_next = ip_num + 1  if ip_num != 8 else 1
    ip1_position = get_IP_position(ip_num)
    ip2_position = get_IP_position(ip_next)
    if ip_next != 1:
        return is_blm_in_ip_neighbourhood(blm, ip_num, -left_offset, ip2_position - ip1_position - right_offset)
    else:
        return is_blm_in_ip_neighbourhood(blm, ip_num, -left_offset, LHC_LENGTH - ip1_position - right_offset)


if __name__ == '__main__':
    number_of_simultaneous_processes = 4
    calculators = [PreOffsetCalc(), PreOffsetCorrectedIntegralCalc(),
                   RawIntegralCalc(),
                   PostOffsetCalc(), PostOffsetCorrectedIntegralCalc(),
                   # PlotCalc(BLM_INTERVALS_PLOTS_DIR)
                   ]
    start = datetime(year=2016, month=3, day=28)
    end = datetime(year=2016, month=10, day=31)
    # start = datetime(year=2017, month=5, day=1)
    # end = datetime(year=2017, month=10, day=16)

    field = 'LOSS_RS12'
    blm_list_file_path = os.path.join(BLM_LIST_DIR, 'allblm_20161013.csv')
    iil = IntensityIntervalsLoader()
    iil.set_files_paths(PICKLE_INTENSITY_INTERVALS_DIR, start, end)
    iil.load_pickles()
    iil.filter_interval_by_dates(start, end)
    iil.filter_interval_by_valid_flag()
    IP_num = 3

    blm_csv_content = {blm.raw_name: blm.position for blm in BLMsParser.read(blm_list_file_path)
                       # if True}
                       if is_blm_in_ip_neighbourhood(blm, IP_num, 100, 100)}
                       # if is_blm_in_arc_after_ip(blm, IP_num, 400, 400)}

    factory = BLMFactory()
    blm_process = BLMProcess(start, end, field, calculators, should_return_blm=True)

    with Pool(processes=number_of_simultaneous_processes) as pool:
        blms = pool.map(blm_process.run, factory.build(iil.data, blm_csv_content))

    if blm_process.should_return_blm:
        for blm in blms:
            print(blm.name, blm.get_pre_oc_dose())

        p = BLMsPlotter('.')
        # p.plot_luminosity_normalized_dose(blms, lambda blm: blm.get_pre_oc_dose(), 39.31)
        # p.plot_intensity_normalized_dose(blms, lambda blm: blm.get_pre_oc_dose(), lambda blm: blm.get_oc_intensity_integral())
        # p.plot_total_cumulated_dose(blms, lambda blm, start, end: blm.get_pre_oc_dose(start, end))
        # p.plot_total_dose(blms, lambda blm: blm.get_pre_oc_dose())
        # p.heat_map_plot(blms)
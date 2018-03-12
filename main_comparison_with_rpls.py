import os
import re
import sys
# Add submodules to path
with open('.gitmodules') as f:
    content = f.read()
    for submodule_dir_name in re.findall(r"^\s*path\s*\=\s(\w+)$", content, re.MULTILINE):
        sys.path.insert(0, submodule_dir_name)

from multiprocessing import Pool
from Common_classes.BLM_classes.BLMsParser import BLMsParser
from config import BLM_LIST_DIR, PICKLE_INTENSITY_INTERVALS_PATH, PLOTS_DIR_PATH
from source.BLMFilter import BLMFilter
from source.Calculators.Integral.BeamModeSubIntervalsCalc import BeamModeSubIntervalsCalc
from source.Calculators.Integral.PostOffsetCorrectedIntegralCalc import PostOffsetCorrectedIntegralCalc
from source.Calculators.Integral.PreOffsetCorrectedIntegralCalc import PreOffsetCorrectedIntegralCalc
from source.Calculators.Integral.RawIntegralCalc import RawIntegralCalc
from source.Calculators.Offset.PostOffsetCalc import PostOffsetCalc
from source.Calculators.Offset.PreOffsetCalc import PreOffsetCalc
from Common_classes.Intensity_classes.IntensityIntervalsLoader import IntensityIntervalsLoader
from source.Plotters.BLMsPlotter import BLMsPlotter
from source.BLMFactory import BLMFactory
from source.BLMProcess import BLMProcess
import logging
from arguments_parser import build_blm_dose_calc_parser
import pandas as pd
from lhc_runs import lhc_runs, extract_runs


def save_to_excel(blms, fname='blms'):
    writer = pd.ExcelWriter(fname + '.xlsx')
    for blm in blms:
        blm.get_as_pandas_dataframe().to_excel(writer,blm.name)
    writer.save()


def save_to_excel_beam_modes(blms, fname):
    writer = pd.ExcelWriter(fname + '.xlsx')
    rslt = pd.concat([blm.get_beam_mode_doses_as_dataframe() for blm in blms], axis=0)
    rslt.to_excel(writer,'data')
    writer.save()


if __name__ == '__main__':

####################################################################################

    parser = build_blm_dose_calc_parser()
    args = parser.parse_args()
    # print(args)

############################## Parsed command line arguments assignment ########
    runs = extract_runs(args)
    start = runs[0][0]
    end = runs[-1][1]

    blm_csv_list_filename = args.file_name
    number_of_simultaneous_processes = args.processes_num
    should_plot_total = args.pt
    should_plot_intensity_norm = args.pi
    should_plot_luminosity_norm = bool(args.pl)
    should_save_excel = args.save_to_excel
    luminosity = args.pl # 39.31 if start.year == 2016 else 37.83
    should_plot_cumsum = args.pcs
    logging_level = getattr(logging, args.logging_level)
    blm_raw_data_dir = args.raw_blm_path
    pickled_blm_dir = args.pickled_blm_path
    field = args.field_name
    IP_num = args.ir if args.ir else args.arc

    blm_filter_function_name = 'ir' if args.ir else None
    blm_filter_function_name = 'arc' if args.arc else None
    if not blm_filter_function_name:
        blm_filter_function_name = 'all'

    should_plot_heatmap = False
    left_offset = 700
    right_offset = 700

####################################################################################
    logging.basicConfig(level=logging_level)

    calculators = [PreOffsetCalc(), PreOffsetCorrectedIntegralCalc(),
                   RawIntegralCalc(),
                   PostOffsetCalc(), PostOffsetCorrectedIntegralCalc(),
                   BeamModeSubIntervalsCalc()
                   # PlotCalc(BLM_INTERVALS_PLOTS_DIR)
                   ]

    # Intensity files loading
    iil = IntensityIntervalsLoader()
    iil.set_files_paths(PICKLE_INTENSITY_INTERVALS_PATH, start, end)
    iil.load_pickles()
    iil.filter_interval_by_dates(runs)
    # iil.filter_interval_by_valid_flag()

    # B
    blm_list_file_path = os.path.join(BLM_LIST_DIR, blm_csv_list_filename)
    blm_filter = BLMFilter()
    blms = BLMsParser.read(blm_list_file_path)
    filtered_blms = blm_filter.filter_blms(blms, func=blm_filter.get_filter_function(blm_filter_function_name, IP_num, left_offset, right_offset))
    should_plot = should_plot_total or should_plot_cumsum or should_plot_intensity_norm or should_plot_luminosity_norm or True
    should_return_blm = should_plot or should_save_excel
    blm_process = BLMProcess(start, end, field, calculators, should_return_blm,blm_raw_data_dir, pickled_blm_dir)

    # Reading and processing BLMs data
    with Pool(processes=number_of_simultaneous_processes) as pool:
        blms = [blm for blm in pool.map(blm_process.run, BLMFactory.build(iil.data, filtered_blms)) if blm is not None]

    if blm_process.should_return_blm:

        logging.info('Analysed BLM types: {}'.format(', '.join(set(blm.get_blm_type() for blm in blms))))

        if should_save_excel and blms:
            save_to_excel_beam_modes(blms, 'BLMs_with_beam_modes_{}_{}'.format(start.strftime('%Y%m%d'), end.strftime('%Y%m%d')))

        if should_plot:
            # Plotting
            p = BLMsPlotter('.')
            if should_plot_luminosity_norm:
                p.plot_luminosity_normalized_dose(blms, lambda blm: blm.get_pre_oc_dose(), luminosity)
            if should_plot_intensity_norm:
                p.plot_intensity_normalized_dose(blms, lambda blm: blm.get_pre_oc_dose(), lambda blm: blm.get_oc_intensity_integral())
            if should_plot_cumsum:
                p.plot_total_cumulated_dose(blms, lambda blm, start, end: blm.get_pre_oc_dose(start, end))
            if should_plot_total:
                p.plot_total_dose(blms, lambda blm: blm.get_pre_oc_dose())
            if should_plot_heatmap:
                p.heat_map_plot(blms)
            p.plot_total_dose_with_rpls(blms, lambda blm: blm.get_pre_oc_dose())
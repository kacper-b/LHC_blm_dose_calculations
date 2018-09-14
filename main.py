import os
import re
import sys
# Add submodules to path
from datetime import datetime


with open('.gitmodules') as f:
    content = f.read()
    for submodule_dir_name in re.findall(r"^\s*path\s*\=\s(\w+)$", content, re.MULTILINE):
        if submodule_dir_name != 'LHC_runs':
            sys.path.insert(0, submodule_dir_name)
from Common_classes.DBConnector import DBConnector, BLM, BeamInterval, Run, BeamMode
from multiprocessing import Pool
from source.Plotters.PlotCalc import PlotCalc

# from config import BLM_LIST_DIR, PICKLE_INTENSITY_INTERVALS_PATH, PLOTS_DIR_PATH
from source.Calculators.Integral.BeamModeSubIntervalsCalc import BeamModeSubIntervalsCalc
from source.Calculators.Integral.PostOffsetCorrectedIntegralCalc import PostOffsetCorrectedIntegralCalc
from source.Calculators.Integral.PreOffsetCorrectedIntegralCalc import PreOffsetCorrectedIntegralCalc
from source.Calculators.Integral.RawIntegralCalc import RawIntegralCalc
from source.Calculators.Offset.PostOffsetCalc import PostOffsetCalc
from source.Calculators.Offset.PreOffsetCalc import PreOffsetCalc
# from source.Plotters.BLMsPlotter import BLMsPlotter
from source.BLMProcess import BLMProcess
import logging
from arguments_parser import build_blm_dose_calc_parser
import pandas as pd
# from lhc_runs import lhc_runs, extract_runs

BLM_LIST_DIR = '/mnt/monitoring_analysis/data/blm_lists'

def save_to_excel(blms, fname='blms'):
    writer = pd.ExcelWriter(fname + '.xlsx')
    for blm in blms:
        blm.get_as_pandas_dataframe().to_excel(writer,blm.name)
    writer.save()

def save_to_excel_beam_modes(blms, fname, all_beam_modes):
    writer = pd.ExcelWriter(fname + '.xlsx')
    rslt = pd.concat([blm.get_beam_mode_doses_as_dataframe(all_beam_modes) for blm in blms], axis=0)
    rslt.to_excel(writer,'data')
    writer.save()


if __name__ == '__main__':
    dbc_test = DBConnector('pcen35754', db_name='lhc_raw', user='jenkins')
    dbc_test.read_password_from_the_file('jenkins_password')
    dbc_test.connect_to_db()
    dbc_test.build_database()
    dbc_test.commit()
    runs = list(dbc_test.get_lhc_runs())
####################################################################################

    parser = build_blm_dose_calc_parser(runs)
    args = parser.parse_args()
    # print(args.start_date)

    dbc_test.close()
############################# Parsed command line arguments assignment ########
    # runs = Run.extract_runs(args)
    # start = runs[0][0]
    # end = runs[-1][1]
    requested_run = Run.extract_runs_from_command_line_argument(args, runs)
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

# ####################################################################################
    logging.basicConfig(level=logging_level)

    calculators = [PreOffsetCalc(), PreOffsetCorrectedIntegralCalc(),
                   RawIntegralCalc(),
                   PostOffsetCalc(), PostOffsetCorrectedIntegralCalc(),
                   BeamModeSubIntervalsCalc(),
                   # PlotCalc('plots')
                   ]


    dbc_test.connect_to_db()
    dbc_test.build_database()
    dbc_test.commit()

    if blm_csv_list_filename is not None:
        # blms_list = ['BLMED.04R8.B2C10_TDI.4R8.B2', ]
        blm_list_file_path = os.path.join(BLM_LIST_DIR, blm_csv_list_filename)
        blms_list = pd.read_csv(blm_csv_list_filename, header=None)[0].values
        filter_func = BLM.name.in_(blms_list)
    else:
        filter_func = True

    blms = list(dbc_test.session.query(BLM).filter(filter_func).all())
    # blms =list(filter(lambda  blm: '16L2' in blm.name or '17L2' in blm.name or '15L2' in blm.name, blms))
    print(len(blms))
    beam_modes = list(dbc_test.session.query(BeamMode))
    beam_intervals = list(filter(lambda beam_interval: beam_interval.start_time in requested_run, dbc_test.session.query(BeamInterval).all()))
    dbc_test.close()


    should_plot = should_plot_total or should_plot_cumsum or should_plot_intensity_norm or should_plot_luminosity_norm
    should_return_blm = should_plot or should_save_excel
    blm_process = BLMProcess(requested_run, field, calculators, should_return_blm, dbc_test, beam_intervals)
    # Reading and processing BLMs data
    with Pool(processes=number_of_simultaneous_processes) as pool:
        blm_names_blm_intervals = {pseudoBLM.name: pseudoBLM.blm_intervals for pseudoBLM in pool.map(blm_process.run, blms[:]) if pseudoBLM is not None}

    if blm_process.should_return_blm:

        blm_names = set(blm_names_blm_intervals.keys())
        for blm in blms:
            # print(blm.name, blm_names)
            if blm.name in blm_names:
                blm.blm_intervals_filtered = blm_names_blm_intervals[blm.name]
                # for i in blm.blm_intervals_filtered:
                #     print('{:%Y-%m-%d %H:%M}\t{:%Y-%m-%d %H:%M}\t{:.3e}\t{:.3e}'.format(i.start_time, i.end_time, i.integrated_dose, i.offset_pre))
            else:
                blm.blm_intervals_filtered = []
                # sys.exit()
        logging.info('Analysed BLM types: {}'.format(', '.join(set(blm.get_blm_type() for blm in blms))))

        if should_save_excel and blms:
            # save_to_excel_beam_modes(blms, 'BLMs_with_beam_modes_{}'.format(requested_run),beam_modes)
            save_to_excel_beam_modes(blms, 'BLMs_with_beam_modes_{:%Y%m%d}_{:%Y%m%d}'.format(requested_run.get_earliest_date(), requested_run.get_latest_date()),beam_modes)

        if should_plot:
            # Plotting
            pass
            # p = BLMsPlotter('.')
            # if should_plot_luminosity_norm:
            #     p.plot_luminosity_normalized_dose(blms, lambda blm: blm.get_pre_oc_dose(), luminosity)
            # if should_plot_intensity_norm:
            #     p.plot_intensity_normalized_dose(blms, lambda blm: blm.get_pre_oc_dose(), lambda blm: blm.get_oc_intensity_integral())
            # if should_plot_cumsum:
            #     p.plot_total_cumulated_dose(blms, lambda blm, start, end: blm.get_pre_oc_dose(start, end))
            # if should_plot_total:
            #     p.plot_total_dose(blms, lambda blm: blm.get_pre_oc_dose())
            # if should_plot_heatmap:
            #     p.heat_map_plot(blms)
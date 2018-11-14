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
from Common_classes.DBConnector import DBConnector, BLM, BeamInterval, Run, BeamMode, BLMInterval
from multiprocessing import Pool
from source.Plotters.PlotCalc import PlotCalc

# from config import BLM_LIST_DIR, PICKLE_INTENSITY_INTERVALS_PATH, PLOTS_DIR_PATH
from source.Calculators.Integral.BeamModeSubIntervalsCalc import BeamModeSubIntervalsCalc
from source.Calculators.Integral.PostOffsetCorrectedIntegralCalc import PostOffsetCorrectedIntegralCalc
from source.Calculators.Integral.PreOffsetCorrectedIntegralCalc import PreOffsetCorrectedIntegralCalc
from source.Calculators.Integral.RawIntegralCalc import RawIntegralCalc
from source.Calculators.Offset.PostOffsetCalc import PostOffsetCalc
from source.Calculators.Offset.PreOffsetCalc import PreOffsetCalc
from source.Plotters.BLMsPlotter import BLMsPlotter
from source.BLMProcess import BLMProcess
import logging
from arguments_parser import build_blm_dose_calc_parser
import pandas as pd
# from lhc_runs import lhc_runs, extract_runs

# BLM_LIST_DIR = '/mnt/monitoring_analysis/data/blm_lists'

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
    dbc_test = DBConnector('pcen35754', db_name='lhc_raw', user='grafanareader')
    # dbc_test.read_password_from_the_file('grafanareader_password')
    dbc_test.connect_to_db()
    # dbc_test.build_database()
    # dbc_test.commit()
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



    dbc_test.connect_to_db()
    dbc_test.build_database()
    dbc_test.commit()

    if blm_csv_list_filename is not None:
        blms_list = pd.read_csv(blm_csv_list_filename, header=None)[0].values
        filter_func = BLM.name.in_(blms_list)
    else:
        filter_func = True

    blms = list(dbc_test.session.query(BLM).filter(filter_func).all())
    beam_modes = list(dbc_test.session.query(BeamMode))
    beam_intervals = list(filter(lambda beam_interval: beam_interval.start_time in requested_run, dbc_test.session.query(BeamInterval).all()))


    should_plot = should_plot_total or should_plot_cumsum or should_plot_intensity_norm or should_plot_luminosity_norm
    should_return_blm = should_plot or should_save_excel

    if should_return_blm:
        for blm in blms:
            blm = dbc_test.session.query(type(blm)).populate_existing().get(blm.name)
            blm.blm_intervals_filtered = blm.blm_intervals.filter(BLMInterval.start_time >= requested_run.get_earliest_date()). \
                filter(BLMInterval.start_time <= requested_run.get_latest_date()).all()

        logging.info('Analysed BLM types: {}'.format(', '.join(set(blm.get_blm_type() for blm in blms))))
        # dbc_test.close()
        if should_save_excel and blms:
            save_to_excel_beam_modes(blms, 'BLMs_with_beam_modes_{}'.format(requested_run.get_representation_for_filename()),beam_modes)
        if should_plot:
            pass
            p = BLMsPlotter('.', blm_csv_list_filename=blm_csv_list_filename.split(os.sep)[-1].replace('.csv',''))
            if should_plot_total:
                p.plot_total_dose(blms, lambda blm: blm.get_pre_oc_dose(), requested_run)

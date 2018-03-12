import argparse
from config import PICKLE_BLM_INTERVALS_DIR, BLM_DATA_DIR
from datetime import datetime
from dateutil import tz
from tools.workers import str2datetime
from lhc_runs import lhc_runs
utc = tz.tzutc()

def build_blm_dose_calc_parser():
    """
    Function which reads
    :return argparse.ArgumentParser: command line arguments
    """

    start = datetime(year=2017, month=4, day=29)
    end = datetime.today()
    blm_csv_list_filename = 'ruben_07032018.csv' #'151617L2_ti_qi_ei_bi.csv' #

    parser = argparse.ArgumentParser(description='BLM doses calculator')
    date_parser = lambda str_date: str2datetime(str_date, '%d-%m-%Y')

    parser.add_argument("-e", "--end_date", help="provide end date of analysed period, will be used only if START_DATE is specified", type=date_parser, default=end)

    run_type_group = parser.add_mutually_exclusive_group(required=True)
    run_type_group.add_argument("-s", "--start_date", help="provide start date of analysed period", type=date_parser, default=start)
    for run in lhc_runs:
        run_type_group.add_argument('-{}'.format(run.shortcut), '--{}'.format(run.name), help=str(run), action="store_const", const=run.dates)
        run_type_group.add_argument_group()

    parser.add_argument("-var", "--field_name", help="Timber variable name", type=str, default='LOSS_RS12', choices=['LOSS_RS12', 'LOSS_RS09', 'DOSE_INT_HH'])
    parser.add_argument("-n", "--processes_num", help="Number of simultaneous processes", type=int, default=8)
    parser.add_argument("-f", "--file_name", help="BLM list file name", type=str, default=blm_csv_list_filename)
    parser.add_argument("-l", "--logging_level", help="Logging level", type=str, default='CRITICAL',
                        choices=['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    parser.add_argument("-raw", "--raw_blm_path", help="Path to directory with all raw BLM data", default=BLM_DATA_DIR)
    parser.add_argument("-pkl", "--pickled_blm_path", help="Path to directory with all calculated and pickled BLMs", default=PICKLE_BLM_INTERVALS_DIR)

    parser.add_argument("-pl", help="Plot total integrated dose normalized with given luminosity", type=float)
    parser.add_argument("-pt", help="Plot total integrated dose", action="store_true")
    parser.add_argument("-pi", help="Plot total integrated dose normalized with the integrated intensity", action="store_true")
    parser.add_argument("-ex", "--save_to_excel", help="Save doses to an excel file", action="store_true")
    parser.add_argument("-pcs", help="Plot cumulative sums", action="store_true")
    parser.add_argument("-ptlim", help="Yrange for the TID plot", type=eval)

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-arc", help="Arc after given IP will be plotted", type=int, choices=list(range(1, 9)))
    group.add_argument("-ir", help="IR for given IP will be plotted", type=int, choices=list(range(1, 9)))
    return parser
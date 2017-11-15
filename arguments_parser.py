import argparse
from datetime import datetime
from config import PICKLE_BLM_INTERVALS_DIR, BLM_DATA_DIR


def build_blm_dose_calc_parser():
    """
    Function which reads
    :return argparse.ArgumentParser: command line arguments
    """
    start = datetime(year=2016, month=3, day=28)
    end = datetime(year=2016, month=10, day=31)
    start = datetime(year=2017, month=5, day=1)
    end = datetime(year=2017, month=10, day=16)
    blm_csv_list_filename = 'all_blms_dcum_meters_ti_qi_ei_bi.csv' #'151617L2_ti_qi_ei_bi.csv' #

    parser = argparse.ArgumentParser(description='BLM doses calculator')
    date_parser = lambda str_date: datetime.strptime(str_date, '%d-%m-%Y')

    parser.add_argument("-s", "--start_date", help="provide start date of analysed period", type=date_parser, default=start)
    parser.add_argument("-e", "--end_date", help="provide end date of analysed period", type=date_parser, default=end)
    parser.add_argument("-var", "--field_name", help="Timber variable name", type=str, default='LOSS_RS12', choices=['LOSS_RS12', 'LOSS_RS09', 'DOSE_INT_HH'])
    parser.add_argument("-n", "--processes_num", help="Number of simultaneous processes", type=int, default=8)
    parser.add_argument("-f", "--file_name", help="BLM list file name", type=str, default=blm_csv_list_filename)
    parser.add_argument("-l", "--logging_level", help="Logging level", type=str, default='CRITICAL',
                        choices=['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    parser.add_argument("-raw", "--raw_blm_path", help="Path to directory with all raw BLM data", default=BLM_DATA_DIR)
    parser.add_argument("-pkl", "--pickled_blm_path", help="Path to directory with all calculated and pickled BLMs", default=PICKLE_BLM_INTERVALS_DIR)

    parser.add_argument("-pl", help="Plot total integrated dose normalized with given luminosity", type=float)
    parser.add_argument("-pt", help="Plot total integrated dose", action="store_true")
    parser.add_argument("-pi", help="Plot total integrated dose", action="store_true")
    parser.add_argument("-pcs", help="Plot cumulative sums", action="store_true")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-arc", help="Arc after given IP will be plotted", type=int, choices=list(range(1, 9)))
    group.add_argument("-ir", help="IR for given IP will be plotted", type=int, choices=list(range(1, 9)))
    return parser
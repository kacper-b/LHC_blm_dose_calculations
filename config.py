import os
import sys
import re

PARENT_DIR_PATH = '/media/sf_work/monitoring_analysis'

sys.path.append(PARENT_DIR_PATH)
DATA_DIR_PATH = os.path.join(PARENT_DIR_PATH, 'data')

__dirs = os.listdir(DATA_DIR_PATH)
__DATA_DIR_NAME = 'data'
__RESULT_DIR_NAME = 'results'
DATA_DIRs_NAMES = {dir_name: os.path.join(DATA_DIR_PATH, dir_name) for dir_name in __dirs}
PICKLE_INTENSITY_INTERVALS_DIR = os.path.join(DATA_DIRs_NAMES['pickles'], 'intensity_intervals')
BLM_DATA_DIR = DATA_DIRs_NAMES['blm_data_2016']
BLM_LIST_DIR = DATA_DIRs_NAMES['blm_lists']
BLM_FILES_REGEX_PATTERN = re.compile(
    r".*\/([\w\-]+)_(\d{4}(?:_?)\d{2}(?:_?)\d{2})\d*_(\d{4}(?:_?)\d{2}(?:_?)\d{2}).*(LOSS_RS\d\d|DOSE_INT_HH)\.(?:p|pkl)")
INTENSITY_INTERVALS_FILES_REGEX_PATTERN = re.compile(r".*_(\d{8})\d*_(\d{8})\d*\.p")
BLM_DATE_FORMAT = '%Y_%m_%d'
PICKLE_BLM_INTERVALS_DIR = os.path.join(DATA_DIRs_NAMES['pickles'], 'analysed_blm_2016')
BLM_INTERVALS_PLOTS_DIR = PICKLE_BLM_INTERVALS_DIR
INTENSITY_INTERVALS_DATE_FORMAT = '%Y%m%d'
IPs = [[0, 1, 'IP1', 1],
       [3332.360, 2, 'IP2', 1],
       [6664.720, 3, 'IP3', 0],
       [9997.081, 4, 'IP4', 1],
       [13329.441, 5, 'IP5', 1],
       [16661.802, 6, 'IP6', 1],
       [19994.162, 7, 'IP7', 1],
       [23315.302, 8, 'IP8', 1],]
LHC_LENGTH = 26658.883 #in meters
TIMBER_LOGGING_FREQ = 84
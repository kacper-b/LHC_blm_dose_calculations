import os
import sys
import re

PARENT_DIR_PATH = '/media/sf_monitoring_analysis'

# sys.path.append(PARENT_DIR_PATH)
DATA_DIR_PATH = os.path.join(PARENT_DIR_PATH, 'data')

__dirs = os.listdir(DATA_DIR_PATH)
__DATA_DIR_NAME = 'data'
__RESULT_DIR_NAME = 'results'
RESULT_DIR_PATH = os.path.join(PARENT_DIR_PATH, __RESULT_DIR_NAME,'plots')
DATA_DIRs_NAMES = {dir_name: os.path.join(DATA_DIR_PATH, dir_name) for dir_name in __dirs}
PICKLE_INTENSITY_INTERVALS_DIR = os.path.join(DATA_DIRs_NAMES['pickles'], 'intensity_intervals')
BLM_DATA_DIR = DATA_DIRs_NAMES['blm_data_2017']
BLM_LIST_DIR = DATA_DIRs_NAMES['blm_lists']
# BLM_FILES_REGEX_PATTERN = re.compile(
#     r".*\/([\w\-]+)_(\d{4}(?:_?)\d{2}(?:_?)\d{2})\d*_(\d{4}(?:_?)\d{2}(?:_?)\d{2}).*(LOSS_RS\d\d|DOSE_INT_HH)\.(?:p|pkl)")

INTENSITY_INTERVALS_FILES_REGEX_PATTERN = re.compile(r".*_(\d{8})\d*_(\d{8})\d*\.p")
BLM_DATE_FORMAT = '%Y_%m_%d'
PICKLE_BLM_INTERVALS_DIR = os.path.join(DATA_DIRs_NAMES['pickles'], 'analysed_blm')
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
ARC_DISTANCE_OFFSET = 400
LHC_LENGTH = 26658.883 #in meters
BLM_TYPE_REGEX_PATERN = re.compile(r"BLM(.+?)\.")

TIMBER_LOGGING_FREQ = 84
INTENSITY_NORMALIZED_PLOT_YRANGE = (1e-24, 5e-17)
LUMINOSITY_NORMALIZED_PLOT_YRANGE = (1e-3, 1e+4)

BEAM_MODES = {1: 'NO MODE',
              2: 'SETUP',
              3: 'INJECTION PROBE BEAM',
              4: 'INJECTION SETUP BEAM',
              5: 'INJECTION PHYSICS BEAM',
              6: 'PREPARE RAMP',
              7: 'RAMP',
              8: 'FLAT TOP',
              9: 'SQUEEZE',
              10: 'ADJUST',
              11: 'STABLE BEAMS',
              12: 'UNSTABLE BEAMS',
              13: 'BEAM DUMP',
              14: 'RAMP DOWN',
              15: 'RECOVERY',
              16: 'INJECT AND DUMP',
              17: 'CIRCULATE AND DUMP',
              18: 'ABORT',
              19: 'CYCLING',
              20: 'BEAM DUMP WARNING',
              21: 'NO BEAM',
              22: 'PREPARE INJECTION',}
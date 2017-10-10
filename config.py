import os
import sys
import re

PARENT_DIR_PATH = '/media/sf_work/monitoring_analysis'

sys.path.append(PARENT_DIR_PATH)
DATA_DIR_PATH = os.path.join(PARENT_DIR_PATH, 'data')

__dirs = os.listdir(DATA_DIR_PATH)
DATA_DIRs_NAMES = {dir_name: os.path.join(DATA_DIR_PATH, dir_name) for dir_name in __dirs}
PICKLE_INTENSITY_INTERVALS_DIR = os.path.join(DATA_DIRs_NAMES['pickles'], 'intensity_intervals')
BLM_DATA_DIR = DATA_DIRs_NAMES['blm_data']
BLM_LIST_DIR = DATA_DIRs_NAMES['blm_lists']
BLM_FILES_REGEX_PATTERN = re.compile(
    r".*\/(\w+)_(\d{4}(?:_?)\d{2}(?:_?)\d{2})\d*_(\d{4}(?:_?)\d{2}(?:_?)\d{2}).*(LOSS_RS\d\d|DOSE_INT_HH)\.p")
INTENSITY_INTERVALS_FILES_REGEX_PATTERN = re.compile(r".*_(\d{8})\d*_(\d{8})\d*\.p")
BLM_DATE_FORMAT = '%Y_%m_%d'
PICKLE_BLM_INTERVALS_DIR = os.path.join(DATA_DIRs_NAMES['pickles'], 'analysed_blm')
BLM_INTERVALS_PLOTS_DIR = PICKLE_BLM_INTERVALS_DIR
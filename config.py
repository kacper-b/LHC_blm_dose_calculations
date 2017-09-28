import os
import sys

PARENT_DIR_PATH = '/media/sf_work/monitoring_analysis'

sys.path.append(PARENT_DIR_PATH)
DATA_DIR_PATH = os.path.join(PARENT_DIR_PATH, 'data')
__dirs = os.listdir(DATA_DIR_PATH)
DATA_DIRs_NAMES = {dir_name: os.path.join(DATA_DIR_PATH, dir_name) for dir_name in __dirs}
PICKLE_INTENSITY_INTERVALS_PATH = os.path.join(DATA_DIRs_NAMES['pickles'], 'intensity_intervals')

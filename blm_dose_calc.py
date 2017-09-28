import pandas as pd
import numpy as np
import os
import sys
import pickle
import random
import time
from decimal import Decimal
from statsmodels.nonparametric.smoothers_lowess import lowess

from blm_data import *


from config import DATA_DIRs_NAMES, PICKLE_INTENSITY_INTERVALS_PATH


print(DATA_DIRs_NAMES)



iil = intensity_interval_loader(PICKLE_INTENSITY_INTERVALS_PATH, 2016)
iil.file_lister()


iil.file = iil.files[3]

iil.file_loader()






dir_names = ['BLMEI_04R6_B2I10_MSDA_C4R6_B2',
             'BLMQI_13R8_B2E30_MQ',
             'BLMQI_16L8_B1E30_MQ',
             'BLMQI_19L1_B2E30_MQ',
             'BLMQI_32R2_B2E30_MQ',
             'BLMTI_04L5_B2E10_TANC_4L5',
             'BLMTI_04R5_B1E10_TANC_4R5']


for blm_name in dir_names:
    start = time.time()
#     direct =  os.path.join(DATA_DIRs_NAMES['blm_data'],blm_name)

    b = blm_data(DATA_DIRs_NAMES['blm_data'],blm_name,'2016')
    b.flag_full = 1
    b.flag_print = 1
    b.flag_force_save = 1
    b.pp(b.name)

    b.blm_data_file_lister()

    b.flag_print = 0
    b.blm_data_loader()

    b.blm_interval_analysis(iil.intervals)
    direct_pickle = os.path.join(DATA_DIRs_NAMES['pickles'],'analysed_blm',blm_name+'.p')

    b.pickler(direct_pickle)
    end = time.time()

    print(end-start)

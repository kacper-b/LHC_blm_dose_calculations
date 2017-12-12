import os
import re
from datetime import datetime
import time
from config import *
import matplotlib
matplotlib.use('agg') 
import matplotlib.gridspec as gridspec
import matplotlib.dates as md
import matplotlib.colors as colors
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from projects.Plotting.python.plotting_layout import plotter_layout, PLOT_DIR
import config
from tools.workers import str2datetime
import matplotlib.dates as mdates
import matplotlib.patches as patches

import matplotlib.pyplot as plt
# from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
matplotlib.style.use('ggplot')
# %matplotlib inline



PLOT_DIR = os.path.join(PARENT_DIR_PATH,'results','plots')
SCHEDULE_PATH = os.path.join(DATA_DIR_PATH,'schedules')

# from source.Plotters.IPlotter import IPlo




class schedule():
    # TODO: Needs to be cleaned up & commented
    def __init__(self,year = 2017):
        SCHEDULE_PATH = os.path.join(DATA_DIR_PATH, 'schedules')
        schedule_dict = {2017: 'LHC_schedule_2017.csv',
                         2016: 'LHC_schedule_2016.csv'}
        with open(os.path.join(SCHEDULE_PATH, schedule_dict[year]), 'r') as f:
            self.df_schedule = pd.read_csv(f)

    def schedule_plotter(self,ax):


        for i, r in self.df_schedule.iterrows():

            start = str2datetime(r['start'], '%Y-%m-%d')
            end = str2datetime(r['end'], '%Y-%m-%d')
            col = r['color']
            text = r['info']
            # convert to matplotlib date representation
            start = mdates.date2num(start)
            end = mdates.date2num(end)
            width = end - start
            height = ax.get_ylim()[1]

            ax.add_patch(
                patches.Rectangle(
                #             (s-length/2, -width/2),   # (x,y)
                (start, 0),
                end,  # width
                height,  # height
                color=col[:],
                alpha=1
                ))
            ax.text(start, 0.95 * height, text, ha='left', va='top', color='k', fontsize=12, rotation=90)


if __name__ == "__main__":


    sc = schedule(2017)

    blm_intervals_start = datetime.strptime('2017-05-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    blm_intervals_end = datetime.strptime('2017-11-30 00:00:00', '%Y-%m-%d %H:%M:%S')

    # fig = plt.figure(figsize=(20, 5))
    f, ax = plt.subplots(1, 1, figsize=[24, 16])
    xfmt = md.DateFormatter('%Y-%m-%d')
    ax.xaxis.set_major_formatter(xfmt)
    ax.xaxis_date()
    ax.set_xlim(blm_intervals_start, blm_intervals_end)
    ax.set_ylim(0, 10)
    f.autofmt_xdate()
    plt.xlabel(r'Date')
    ax.grid(True)


    sc.schedule_plotter(ax)

    f.savefig(os.path.join(PLOT_DIR,'test_1.pdf'))
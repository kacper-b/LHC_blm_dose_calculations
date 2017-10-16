from source.Calculators.Calc import Calc
from datetime import datetime
import os

import matplotlib.dates as md
import matplotlib.pyplot as plt
import pandas as pd
import re
from source.Plotters.IPlotter import IPlotter

class PlotCalc(Calc, IPlotter):
    regex_name_pattern = re.compile(r"([\w\.]+):(\w+)")
    date_format = '%Y_%m_%d_%H%M'

    def __init__(self, output_directory):
        self.output_directory = output_directory

    def run(self, data, blm_intervals):
        col_name = data.columns[0]
        intervals_to_be_plotted = filter(self.should_plot, blm_intervals)
        for blm_interval in intervals_to_be_plotted:
            self.__plotter(col_name, blm_interval,data)
    
    def should_plot(self, blm_interval):
        return bool(blm_interval.should_plot)

    def get_plot_file_name(self, blm_timber_query, blm_interval):
        name_field = re.match(PlotCalc.regex_name_pattern, blm_timber_query)
        if name_field:
            name = name_field.group(1).replace('.', '_')
            field = name_field.group(2)
            start = datetime.utcfromtimestamp(blm_interval.start).strftime(PlotCalc.date_format)
            end = datetime.utcfromtimestamp(blm_interval.end).strftime(PlotCalc.date_format)
            return '{0}_{1}_{2}_{3}'.format(name, start, end, field)

    def __plotter(self, blm_name, blm_interval,data):

        file_name = self.get_plot_file_name(blm_name, blm_interval)+'.svg'
        plot_file_path = os.path.join(self.output_directory, file_name)

        # Plot parameters
        f, ax = plt.subplots(1, 1, figsize=[15, 9])
        xfmt = md.DateFormatter('%m-%d %H:%M')
        ax.xaxis.set_major_formatter(xfmt)
        f.autofmt_xdate()

        plotted_data = self.__blm_data_plot(blm_name, blm_interval, data)
        plotted_pre_oc = self.__pre_offset(blm_name, blm_interval, data)
        plotted_post_oc = self.__post_offset(blm_name, blm_interval, data)
        # self.__offset_level_plot(interval)
        # self.__info_box_plot(interval, ax)
        if plotted_data and plotted_pre_oc and plotted_post_oc:
            self.save_plot(plot_file_path)
        self.clear()


    def __pre_offset(self,blm_name, blm_interval, data):
        data_to_plot = blm_interval.get_preoffset_data(data)
        if not data_to_plot.empty:
            plt.plot(pd.to_datetime(data_to_plot.index, unit='s'), data_to_plot[blm_name], 'g-', label='pre_offset')
            return True
        return False

    def __post_offset(self, blm_name, blm_interval, data):
        data_to_plot = blm_interval.get_postoffset_data(data)
        if not data_to_plot.empty:
            plt.plot(pd.to_datetime(data_to_plot.index, unit='s'), data_to_plot[blm_name], 'r--', label='post_offset')
            return True
        return False

    def __blm_data_plot(self,blm_name, blm_interval, data):
        data_to_plot = blm_interval.get_integrated_data(data)
        if not data_to_plot.empty:
            plt.plot(pd.to_datetime(data_to_plot.index, unit='s'), data_to_plot[blm_name], 'b-', label='raw data')
            return True
        return False

    # def __offset_level_plot(self, interval):
    #     plt.plot([datetime.datetime.utcfromtimestamp(interval.start), datetime.datetime.utcfromtimestamp(interval.end)],
    #              interval.offset_mean * np.ones(2), 'y--', label='offset')

    # def __info_box_plot(self, interval, ax):
    #     textstr = 'Start: {0:s}\nEnd: {5:s}\nDuration: {6:}\nFill: {1:d}\nIntensity max: {2:.1e}\nIntensity dump: {3:.2%}\nIntensity loss: {4:.2%}'. \
    #         format(interval.get_start_date(),
    #                interval.filling_number,
    #                interval.max_intensity_offset_corrected,
    #                interval.dumped_intensity_offset_corrected / interval.max_intensity_offset_corrected,
    #                1 - interval.dumped_intensity_offset_corrected / interval.max_intensity_offset_corrected,
    #                interval.get_end_date(),
    #                interval.get_duration())
    #
    #     props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    #     ax.text(0.1, 1.25, textstr, transform=ax.transAxes, fontsize=14, verticalalignment='top', bbox=props)


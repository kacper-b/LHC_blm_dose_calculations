import matplotlib
matplotlib.use('agg')
from source.Calculators.Calc import Calc
from datetime import datetime
import os
import configurations.config
# from tools.workers import second2datetime
import matplotlib.dates as md
import matplotlib.pyplot as plt
import pandas as pd
import re
from source.Plotters.IPlotter import IPlotter

class PlotCalc(Calc, IPlotter):
    """
    The class allows to plot suspected (with should_plot flag set to True) BLM intervals.
    """
    regex_name_pattern = re.compile(r"([\w\.]+)(\w+)")
    date_format = '%Y_%m_%d_%H%M'

    def __init__(self, output_directory):
        """
        :param output_directory: Plots' output directory
        """
        self.output_directory = output_directory

    def run(self, data, blm_intervals):
        """
        It iterates over BLM intervals and
        :param data:
        :param blm_intervals:
        :return:
        """
        col_name = data.columns[0]
        intervals_to_be_plotted = filter(self.should_plot, blm_intervals)
        for blm_interval in intervals_to_be_plotted:
            self.__plotter(col_name, blm_interval,data)

    
    def should_plot(self, blm_interval):
        """
        It returns True if blm_interval is marked as a one that should be plotted.
        :param blm_interval:
        :return bool:
        """
        return True
        return bool(blm_interval.should_plot)

    def get_plot_file_name(self, blm_timber_query, blm_interval):
        """
        It returns the plot file name.
        :param blm_timber_query: BLM_name:field (ex. BLMAI.08L5:LOSS_RS12)
        :param blm_interval: blm interval to be plotted.
        :return:
        """
        # start = blm_interval.start_time.strftime(PlotCalc.date_format)
        # end = .strftime(PlotCalc.date_format)
        return  '{}_{:%Y_%m_%d_%H%M}_{:%Y_%m_%d_%H%M}'.format(blm_interval.blm_name.replace('.', '_'), blm_interval.start_time, blm_interval.end_time)

    def __plotter(self, blm_name, blm_interval,data):
        """
        It plots blm_data and offsets.
        :param blm_name: BLM name, the same as the data column name
        :param blm_interval: blm_interval to be plotted
        :param data: BLM data
        :return:
        """
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
        # if anything has been plotted, save it
        # if plotted_data and plotted_pre_oc and plotted_post_oc:
        self.save_plot(plot_file_path)
        self.clear()


    def __pre_offset(self,blm_name, blm_interval, data):
        """
        It adds pre-offset plot.
        :param blm_name: BLM name, the same as the data column name
        :param blm_interval: blm_interval to be plotted
        :param data: BLM data
        :return:
        """
        data_to_plot = blm_interval.get_preoffset_data(data)
        if not data_to_plot.empty:
            plt.plot(data_to_plot.index, data_to_plot[blm_name], 'g-', label='pre_offset')
            return True
        return False

    def __post_offset(self, blm_name, blm_interval, data):
        """
        It adds post-offset plot.
        :param blm_name: BLM name, the same as the data column name
        :param blm_interval: blm_interval to be plotted
        :param data: BLM data
        :return:
        """
        data_to_plot = blm_interval.get_postoffset_data(data)
        if not data_to_plot.empty:
            plt.plot(data_to_plot.index, data_to_plot[blm_name], 'r--', label='post_offset')
            return True
        return False

    def __blm_data_plot(self,blm_name, blm_interval, data):
        """
        It adds BLM data plot.
        :param blm_name: BLM name, the same as the data column name
        :param blm_interval: blm_interval to be plotted
        :param data: BLM data
        :return:
        """
        data_to_plot = blm_interval.get_integrated_data(data)
        if not data_to_plot.empty:
            plt.plot(data_to_plot.index, data_to_plot[blm_name], 'b-', label='raw data')
            return True
        return False

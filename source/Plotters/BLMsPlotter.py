from source.Calculators.Calc import Calc
from datetime import datetime
import os
import matplotlib.dates as md
import matplotlib.pyplot as plt
import pandas as pd
import re
import numpy as np
from source.Plotters.IPlotter import IPlotter


class BLMsPlotter(IPlotter):
    plt.style.use('ggplot')
    regex_name_pattern = re.compile(r"([\w\.]+):(\w+)")
    date_format = '%Y_%m_%d_%H%M'

    def __init__(self, output_directory):
        self.output_directory = output_directory

    def plot_normalized_dose(self, blms, blm_summing_func, normalization_func):

        integrated_intensity = normalization_func(blms[0])
        print(integrated_intensity)
        integrated_doses = np.zeros(len(blms), dtype=np.float)
        blm_positions = np.zeros(len(blms), dtype=np.float)

        for index, blm in enumerate(blms):
            integrated_doses[index] = blm_summing_func(blm)
            blm_positions[index] = blm.position

        order = blm_positions.argsort()

        f, ax = plt.subplots(1, 1, figsize=[20, 13.5])

        plt.xlabel(r'DCUM [$m$]')
        plt.ylabel(r'normalized TID [$Gy/ps$]')

        plt.semilogy(blm_positions[order] / 1e2, integrated_doses[order] / integrated_intensity, '.-', label='BLM data')
        self.legend()
        self.show()

    def plot_pre_oc_dose(self, blms, blm_summing_func):

        integrated_doses = np.zeros(len(blms), dtype=np.float)
        blm_positions = np.zeros(len(blms), dtype=np.float)

        for index, blm in enumerate(blms):
            integrated_doses[index] = blm_summing_func(blm)
            blm_positions[index] = blm.position

        order = blm_positions.argsort()

        f, ax = plt.subplots(1, 1, figsize=[20, 13.5])

        plt.xlabel(r'DCUM [$km$]')
        plt.ylabel(r'TID [$Gy$]')

        plt.semilogy(blm_positions[order] / 1e2, integrated_doses[order], '.-', label='BLM data')
        self.legend()
        self.show()

    def plot_pre_oc_dose_with_blm_names(self, blms, blm_summing_func):
        integrated_doses = np.zeros(len(blms), dtype=np.float)
        blm_positions = np.zeros(len(blms), dtype=np.float)
        blm_names = []

        for index, blm in enumerate(blms):
            integrated_doses[index] = blm_summing_func(blm)
            blm_positions[index] = blm.position
            blm_names.append(self.remove_field_name(blm.name))
        blm_names = np.array(blm_names)

        f, ax = plt.subplots(1, 1, figsize=[20, 13.5])

        plt.ylabel(r'TID [$Gy$]')
        order = blm_positions.argsort()

        plt.plot(blm_positions[order] / 1e5, integrated_doses[order], '.-', label='BLM data')
        plt.xticks(blm_positions[order] / 1e5, blm_names[order], rotation=90)
        self.legend()
        self.show()

    def heat_map_plot(self, blms):
        dates = pd.date_range(datetime.utcfromtimestamp(blms[0].blm_intervals[0].start), datetime.utcfromtimestamp(blms[0].blm_intervals[-1].end), freq='1D')
        num_of_days = len(dates)
        intens = np.zeros((len(blms), num_of_days - 1))
        blms_pos = np.zeros((len(blms), 1))

        for j, blm in enumerate(blms):
            intens[j] = np.array([blm.get_pre_oc_dose(dates[i], dates[i + 1]) for i in range(len(dates) - 1)])
            blms_pos[j] = blm.position

        x, y = np.meshgrid(np.array((dates - datetime(1970, 1, 1)).total_seconds()[:-1]), blms_pos)
        dates = pd.to_datetime(x.flatten(), unit='s')
        x = np.array(dates).reshape(y.shape)

        f, ax = plt.subplots(1, 1, figsize=[15, 9])
        xfmt = md.DateFormatter('%Y-%m-%d %H:%M')
        ax.xaxis.set_major_formatter(xfmt)
        f.autofmt_xdate()
        plt.xlabel(r'date')
        plt.ylabel(r'position [$m$]')
        plt.pcolormesh(x, y, intens, label='dose')
        plt.colorbar()
        self.legend()
        self.show()

    def get_plot_file_name(self, blm):
        return blm.get_file_name()

    def remove_field_name(self, blm_timber_query):
        blm_timber_query_splitted = blm_timber_query.split(':')
        if len(blm_timber_query_splitted) == 2:
            return blm_timber_query_splitted[0]
        else:
            return blm_timber_query


    # def __plotter(self, blm):
    #
    #     file_name = blm.get_file_name() + '.svg'
    #     plot_file_path = os.path.join(self.output_directory, file_name)
    #
    #     # Plot parameters
    #     f, ax = plt.subplots(1, 1, figsize=[15, 9])
    #     xfmt = md.DateFormatter('%m-%d %H:%M')
    #     ax.xaxis.set_major_formatter(xfmt)
    #     f.autofmt_xdate()
    #
    #     plotted_data = self.__blm_data_plot(blm_name, blm_interval, data)
    #     plotted_pre_oc = self.__pre_offset(blm_name, blm_interval, data)
    #     plotted_post_oc = self.__post_offset(blm_name, blm_interval, data)
    #     # self.__offset_level_plot(interval)
    #     # self.__info_box_plot(interval, ax)
    #     if plotted_data and plotted_pre_oc and plotted_post_oc:
    #         self.__save_plot(plot_file_path)
    #     self.__clear()
    #

if __name__ == '__main__':
    p = BLMsPlotter(None)
    p.plot(None)
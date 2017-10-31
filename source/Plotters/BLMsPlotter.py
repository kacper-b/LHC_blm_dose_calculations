import logging

import matplotlib.gridspec as gridspec

from source.Calculators.Calc import Calc
from datetime import datetime
import os
import matplotlib.dates as md
import matplotlib.pyplot as plt
import pandas as pd
import re
import numpy as np
from source.Plotters.IPlotter import IPlotter
from projects.Plotting.python.plotting_layout import plotter_layout, PLOT_DIR

class BLMsPlotter(IPlotter):
    """
    Tools to plot dose and normalized dose for specific blms.
    """
    regex_name_pattern = re.compile(r"([\w\.]+):(\w+)")
    date_format = '%Y-%m-%d'

    def __init__(self, output_directory):
        self.output_directory = output_directory
        self.pl = plotter_layout()

    def build_blm_layout(self, dcum_start, dcum_end):
        """

        :param dcum_start:
        :param dcum_end:
        :return: t
        """
        pl = self.pl
        pl.start, pl.end = dcum_start, dcum_end
        pl.x_off = 0
        fig_size = [24, 16]
        fig = plt.figure(figsize=fig_size)
        fig.subplots_adjust(hspace=.001)
        plt.subplots_adjust(hspace=.001)
        plt.subplots_adjust(top=0.95)
        gs1 = gridspec.GridSpec(3, 1)

        # ax1 = fig.add_subplot(2, 1, 1)
        #
        # ax2 = fig.add_subplot(4, 1, 3,sharex=ax1)
        # pl.plotter_layout(ax2, 0, 1)
        #
        # ax3 = fig.add_subplot(4, 1, 4,sharex=ax1)
        # pl.plotter_optics(ax3, ['BETX', 'DX'])
        # return fig, ax1

        # ax1 = fig.add_subplot(3, 1, 1, rowspan=2)
        ax1 = plt.subplot(gs1[:2])
        # ax2 = fig.add_subplot(3, 1, 3,sharex=ax1)
        ax2 = plt.subplot(gs1[2:],sharex=ax1)

        pl.plotter_layout(ax2, 0, 1)

        # ax3 = fig.add_subplot(4, 1, 4,sharex=ax1)
        # pl.plotter_optics(ax3, ['BETX', 'DX'])
        return plt, ax1


    def plot_luminosity_normalized_dose(self, blms, blm_summing_func, luminosity):
        # it's sufficient to calculate normalization factor for one blm only, since intensity data are the same for all BLMs
        logging.info('Integrated luminosity={}'.format(luminosity))

        blm_positions, integrated_doses, blm_types = self.get_sorted_blm_data(blms, blm_summing_func)
        start, end = self.get_plot_dates(blms)

        dcum_start, dcum_end = self.get_plot_xlim(blm_positions)
        f, ax = self.build_blm_layout(dcum_start, dcum_end)
        f.suptitle(r'Total integrated dose for [{} : {}] normalized with luminosity: {} fb-1'.
                   format(start.strftime(self.date_format), end.strftime(self.date_format), luminosity))
        ax.grid(True)

        ax.set_ylabel(r'normalized TID [$Gy/ps$]', fontsize = 12)
        integrated_doses = integrated_doses / luminosity
        ax.semilogy(blm_positions[blm_types == 1], integrated_doses[blm_types == 1], 'r.-', linewidth=0.1, markersize=10, label='Beam 1')
        ax.semilogy(blm_positions[blm_types == 2], integrated_doses[blm_types == 2], 'b.-', linewidth=0.1, markersize=10, label='Beam 2')
        ax.semilogy(blm_positions[blm_types == 0], integrated_doses[blm_types == 0], 'g.-', linewidth=0.1, markersize=10, label='B0')
        ax.legend()

        # self.show()
        file_path_name_without_extension = os.path.join(PLOT_DIR, 'n_lum_TID{}_{}_dcum_{}_{}'.format(start.strftime(self.date_format), end.strftime(self.date_format),int(dcum_start), int(dcum_end)))
        self.save_plot(file_path_name_without_extension + '.png')
        self.save_plot(file_path_name_without_extension + '.pdf')
        self.save_plot_data(file_path_name_without_extension + '.txt', blm_positions, integrated_doses)


    def plot_intensity_normalized_dose(self, blms, blm_summing_func, normalization_func):
        # it's sufficient to calculate normalization factor for one blm only, since intensity data are the same for all BLMs
        integrated_intensity = normalization_func(blms[0])
        logging.info('Integrated intensity={}'.format(integrated_intensity))

        blm_positions, integrated_doses, blm_types = self.get_sorted_blm_data(blms, blm_summing_func)
        start, end = self.get_plot_dates(blms)

        dcum_start, dcum_end = self.get_plot_xlim(blm_positions)
        f, ax = self.build_blm_layout(dcum_start, dcum_end)
        f.suptitle(r'Total integrated dose for [{} : {}] normalized with intensity: {}'.
                   format(start.strftime(self.date_format), end.strftime(self.date_format), integrated_intensity))
        ax.grid(True)

        ax.set_ylabel(r'normalized TID [$Gy/ps$]', fontsize = 12)
        integrated_doses = integrated_doses / integrated_intensity
        ax.semilogy(blm_positions[blm_types == 1], integrated_doses[blm_types == 1], 'r.-', linewidth=0.1, markersize=10, label='Beam 1')
        ax.semilogy(blm_positions[blm_types == 2], integrated_doses[blm_types == 2], 'b.-', linewidth=0.1, markersize=10, label='Beam 2')
        ax.semilogy(blm_positions[blm_types == 0], integrated_doses[blm_types == 0], 'g.-', linewidth=0.1, markersize=10, label='B0')
        ax.legend()

        # self.show()
        file_path_name_without_extension = os.path.join(PLOT_DIR, 'n_int_TID{}_{}_dcum_{}_{}'.format(start.strftime(self.date_format), end.strftime(self.date_format),int(dcum_start), int(dcum_end)))
        self.save_plot(file_path_name_without_extension + '.png')
        self.save_plot(file_path_name_without_extension + '.pdf')
        self.save_plot_data(file_path_name_without_extension + '.txt', blm_positions, integrated_doses)


    def plot_total_dose(self, blms, blm_summing_func):
        # it's sufficient to calculate normalization factor for one blm only, since intensity data are the same for all BLMs

        blm_positions, integrated_doses, blm_types = self.get_sorted_blm_data(blms, blm_summing_func)
        integrated_doses_valid = np.logical_not(np.isnan(integrated_doses))
        blm_positions = blm_positions[integrated_doses_valid]
        integrated_doses = integrated_doses[integrated_doses_valid]
        blm_types = blm_types[integrated_doses_valid]
        start, end = self.get_plot_dates(blms)
        dcum_start, dcum_end = self.get_plot_xlim(blm_positions)
        f, ax = self.build_blm_layout(dcum_start, dcum_end)
        f.suptitle(r'Total integrated dose for [{} : {}]'.format(start.strftime(self.date_format), end.strftime(self.date_format)))
        ax.grid(True)

        ax.set_ylabel(r'TID [$Gy$]')
        ax.semilogy(blm_positions[blm_types==1], integrated_doses[blm_types==1], 'r.-', linewidth=0.1, markersize=10, label='Beam 1')
        ax.semilogy(blm_positions[blm_types==2], integrated_doses[blm_types==2], 'b.-', linewidth=0.1, markersize=10, label='Beam 2')
        ax.semilogy(blm_positions[blm_types==0], integrated_doses[blm_types==0], 'g.-', linewidth=0.1, markersize=10, label='B0')
        ax.legend()

        # self.show()
        file_path_name_without_extension = os.path.join(PLOT_DIR, 'TID{}_{}_dcum_{}_{}'.format(start.strftime(self.date_format), end.strftime(self.date_format),int(dcum_start), int(dcum_end)))
        self.save_plot(file_path_name_without_extension + '.png')
        self.save_plot(file_path_name_without_extension + '.pdf')
        self.save_plot_data(file_path_name_without_extension + '.txt', blm_positions, integrated_doses)


    def plot_total_dose_extrapolated(self, blms, blm_summing_func):

        blm_positions, integrated_doses, blm_types = self.get_sorted_blm_data(blms, blm_summing_func)
        integrated_doses_valid = np.logical_not(np.isnan(integrated_doses))
        blm_positions = blm_positions[integrated_doses_valid]
        integrated_doses = integrated_doses[integrated_doses_valid] * 3000/44.
        blm_types = blm_types[integrated_doses_valid]
        start, end = self.get_plot_dates(blms)
        dcum_start, dcum_end = self.get_plot_xlim(blm_positions)
        f, ax = self.build_blm_layout(dcum_start, dcum_end)
        f.suptitle(r'Extrapolated TID for HL LHC (3000 fb-1) based on BLM data from {} until {} normalized with luminosity (44 fb-1)'.
                   format(start.strftime(self.date_format), end.strftime(self.date_format)),fontsize = 12)
        ax.grid(True)
        f.text(self.pl.start+.5*self.pl.ran, 12, 'PRELIMINARY',fontsize=100,va='center',ha='center', color='gray', alpha=0.5,rotation=45)
        f.text(self.pl.start+.9*self.pl.ran,-7, 'Courtesy MCWG ',fontsize=12,va='bottom',ha='right', color='gray', alpha=0.5,rotation=0)

        ax.set_ylabel(r'Extrapolated TID [$Gy$]')
        ax.semilogy(blm_positions[blm_types==1], integrated_doses[blm_types==1], 'r.-', linewidth=0.1, markersize=10, label='Beam 1')
        ax.semilogy(blm_positions[blm_types==2], integrated_doses[blm_types==2], 'b.-', linewidth=0.1, markersize=10, label='Beam 2')
        # ax.semilogy(blm_positions[blm_types==0], integrated_doses[blm_types==0], 'g.-', linewidth=0.1, markersize=10, label='B0')
        ax.legend()

        # self.show()
        file_path_name_without_extension = os.path.join(PLOT_DIR, 'TID{}_{}_dcum_{}_{}'.format(start.strftime(self.date_format), end.strftime(self.date_format),int(dcum_start), int(dcum_end)))
        self.save_plot(file_path_name_without_extension + '.png')
        self.save_plot(file_path_name_without_extension + '.pdf')
        self.save_plot_data(file_path_name_without_extension + '.txt', blm_positions, integrated_doses)

        return zip(blm_positions, integrated_doses)

    def get_sorted_blm_data(self, blms, blm_summing_func):
        integrated_doses = np.zeros(len(blms), dtype=np.float)
        blm_positions = np.zeros(len(blms), dtype=np.float)
        blm_types = np.zeros(len(blms), dtype=np.float)
        for index, blm in enumerate(blms):
            integrated_doses[index] = blm_summing_func(blm)
            blm_positions[index] = blm.position
            blm_types[index] = self.get_blm_type(blm)
        if -1 in blm_types:
            raise Exception('Wrong recognized BLM type')
        order = blm_positions.argsort()
        return blm_positions[order], integrated_doses[order], blm_types[order]

    def get_plot_dates(self, blms):
        return datetime.utcfromtimestamp(blms[0].blm_intervals[0].start), datetime.utcfromtimestamp(blms[0].blm_intervals[-1].end)

    def get_plot_xlim(self, blm_positions):
        dcum_start = blm_positions[0] - (blm_positions[-1] - blm_positions[0]) * 0.01
        dcum_end = blm_positions[-1] + (blm_positions[-1] - blm_positions[0]) * 0.01
        print(dcum_start, dcum_end)
        return dcum_start, dcum_end

    def get_plot_file_name(self, blm):
        return blm.get_file_name()

    def remove_field_name(self, blm_timber_query):
        blm_timber_query_splitted = blm_timber_query.split(':')
        if len(blm_timber_query_splitted) == 2:
            return blm_timber_query_splitted[0]
        else:
            return blm_timber_query

    def get_blm_type(self, blm):
        blm_type = -1
        if '.B0' in blm.name:
            blm_type = 0
        elif '.B1' in blm.name:
            blm_type = 1
        elif '.B2' in blm.name:
            blm_type = 2
        return blm_type



if __name__ == '__main__':
    p = BLMsPlotter(None)
    p.plot(None)
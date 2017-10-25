import logging

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

    def build_blm_layout(self, dcum_start, dcum_end):
        """

        :param dcum_start:
        :param dcum_end:
        :return: t
        """
        pl = plotter_layout()
        pl.start, pl.end = dcum_start, dcum_end
        pl.x_off = 1
        fig_size = [24, 16]
        f, ax = plt.subplots(3, sharex=True, figsize=fig_size)
        plt.subplots_adjust(hspace=.001)
        plt.subplots_adjust(top=0.95)
        pl.plotter_layout(ax[1], 0, 1)
        pl.plotter_optics(ax[2], ['BETX', 'DX'])
        return f, ax[0]


    def plot_normalized_dose(self, blms, blm_summing_func, normalization_func):
        # it's sufficient to calculate normalization factor for one blm only, since intensity data are the same for all BLMs
        integrated_intensity = normalization_func(blms[0])
        logging.info('Integrated intensity={}'.format(integrated_intensity))

        blm_positions, integrated_doses = self.get_sorted_blm_data(blms, blm_summing_func)
        start, end = self.get_plot_dates(blms)

        dcum_start, dcum_end = self.get_plot_xlim(blm_positions)
        f, ax = self.build_blm_layout(dcum_start, dcum_end)
        f.suptitle(r'Total integrated dose for [{} : {}] normalized with intensity'.format(start.strftime(self.date_format), end.strftime(self.date_format)))
        ax.grid(True)
        # ax.style.use('ggplot')

        ax.set_ylabel(r'normalized TID [$Gy/ps$]',fontsize = 12)
        ax.plot(blm_positions, integrated_doses / integrated_intensity, '.-', linewidth=0.1, markersize=10, label='BLM data')
        ax.legend()

        # self.show()
        self.save_plot(os.path.join(PLOT_DIR, 'nTID{}_{}.pdf'.format(start.strftime(self.date_format), end.strftime(self.date_format))))

    def get_plot_xlim(self, blm_positions):
        dcum_start = blm_positions[0] - (blm_positions[-1] - blm_positions[0]) * 0.01
        dcum_end = blm_positions[-1] + (blm_positions[-1] - blm_positions[0]) * 0.01
        return dcum_start, dcum_end

    def get_sorted_blm_data(self, blms, blm_summing_func):
        integrated_doses = np.zeros(len(blms), dtype=np.float)
        blm_positions = np.zeros(len(blms), dtype=np.float)
        for index, blm in enumerate(blms):
            integrated_doses[index] = blm_summing_func(blm)
            blm_positions[index] = blm.position / 1e2
        order = blm_positions.argsort()
        return blm_positions[order], integrated_doses[order]

    def plot_total_dose(self, blms, blm_summing_func):
        # it's sufficient to calculate normalization factor for one blm only, since intensity data are the same for all BLMs

        blm_positions, integrated_doses = self.get_sorted_blm_data(blms, blm_summing_func)
        start, end = self.get_plot_dates(blms)

        dcum_start, dcum_end = self.get_plot_xlim(blm_positions)
        f, ax = self.build_blm_layout(dcum_start, dcum_end)
        f.suptitle(r'Total integrated dose for [{} : {}]'.format(start.strftime(self.date_format), end.strftime(self.date_format)))

        ax.set_ylabel(r'TID [$Gy$]')
        ax.plot(blm_positions, integrated_doses, '.-', linewidth=0.1, markersize=10, label='BLM data')
        ax.legend()

        # self.show()
        self.save_plot(os.path.join(PLOT_DIR, 'TID{}_{}.pdf'.format(start.strftime(self.date_format), end.strftime(self.date_format))))


    # def heat_map_plot(self, blms):
    #     dates = pd.date_range(datetime.utcfromtimestamp(blms[0].blm_intervals[0].start), datetime.utcfromtimestamp(blms[0].blm_intervals[-1].end), freq='1D')
    #     num_of_days = len(dates)
    #     intens = np.zeros((len(blms), num_of_days - 1))
    #     blms_pos = np.zeros((len(blms), 1))
    #
    #     for j, blm in enumerate(blms):
    #         intens[j] = np.array([blm.get_pre_oc_dose(dates[i], dates[i + 1]) for i in range(len(dates) - 1)])
    #         blms_pos[j] = blm.position
    #
    #     x, y = np.meshgrid(np.array((dates - datetime(1970, 1, 1)).total_seconds()[:-1]), blms_pos)
    #     dates = pd.to_datetime(x.flatten(), unit='s')
    #     x = np.array(dates).reshape(y.shape)
    #
    #     f, ax = plt.subplots(1, 1, figsize=[15, 9])
    #     xfmt = md.DateFormatter('%Y-%m-%d %H:%M')
    #     ax.xaxis.set_major_formatter(xfmt)
    #     f.autofmt_xdate()
    #     plt.xlabel(r'date')
    #     plt.ylabel(r'position [$m$]')
    #     plt.pcolormesh(x, y, intens, label='dose')
    #     plt.colorbar()
    #     self.legend()
    #     self.show()

    def get_plot_dates(self, blms):
        return datetime.utcfromtimestamp(blms[0].blm_intervals[0].start), datetime.utcfromtimestamp(blms[0].blm_intervals[-1].end)


    def get_plot_file_name(self, blm):
        return blm.get_file_name()

    def remove_field_name(self, blm_timber_query):
        blm_timber_query_splitted = blm_timber_query.split(':')
        if len(blm_timber_query_splitted) == 2:
            return blm_timber_query_splitted[0]
        else:
            return blm_timber_query


if __name__ == '__main__':
    p = BLMsPlotter(None)
    p.plot(None)
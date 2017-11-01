import os
import re
from datetime import datetime
import config
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
from projects.Plotting.python.plotting_layout import plotter_layout, PLOT_DIR

from source.Plotters.IPlotter import IPlotter


class BLMsPlotter(IPlotter):
    """
    Tools to plot dose and normalized dose for specific blms.
    """
    regex_name_pattern = re.compile(r"([\w\.]+):(\w+)")
    date_format = '%Y-%m-%d'

    def __init__(self, output_directory):
        self.output_directory = output_directory
        self.layout_plotter = plotter_layout()

    def build_blm_layout(self, dcum_start, dcum_end):
        """

        :param dcum_start:
        :param dcum_end:
        :return: t
        """
        self.layout_plotter.start, self.layout_plotter.end = dcum_start, dcum_end
        self.layout_plotter.x_off = 0
        fig_size = [24, 16]
        fig = plt.figure(figsize=fig_size)
        fig.subplots_adjust(hspace=.001)
        plt.subplots_adjust(hspace=.001)
        plt.subplots_adjust(top=0.95)
        gs1 = gridspec.GridSpec(3, 1)

        ax1 = plt.subplot(gs1[:2])
        ax2 = plt.subplot(gs1[2:], sharex=ax1)
        self.layout_plotter.plotter_layout(ax2, 0, 1)

        # ax3 = fig.add_subplot(4, 1, 4,sharex=ax1)
        # self.layout_plotter.plotter_optics(ax3, ['BETX', 'DX'])

        return plt, ax1

    def plot_luminosity_normalized_dose(self, blms, blm_summing_func, luminosity):
        blm_positions, integrated_doses, blm_types, f, ax, dcum_start, dcum_end, start, end = self.run_common_functions(blm_summing_func, blms)

        f.suptitle(r'Total integrated dose for [{} : {}] normalized with luminosity: {} fb${{^-1}}$'.
                   format(start.strftime(self.date_format), end.strftime(self.date_format), luminosity), fontsize=25)

        ax.set_ylabel(r'normalized TID [Gy/fb$^{-1}$]', fontsize=12)

        self.__plot_blms(blm_positions, integrated_doses / luminosity, blm_types, ax.semilogy)

        file_name = 'n_lum_TID{}_{}_dcum_{}_{}'.format(start.strftime(self.date_format), end.strftime(self.date_format), int(dcum_start), int(dcum_end))
        file_path_name_without_extension = os.path.join(PLOT_DIR, file_name)
        self.save_plot_and_data(file_path_name_without_extension, blm_positions, integrated_doses / luminosity)


    def plot_intensity_normalized_dose(self, blms, blm_summing_func, normalization_func):
        # it's sufficient to calculate normalization factor for one blm only, since intensity data are the same for all BLMs
        integrated_intensity = normalization_func(blms[0])

        blm_positions, integrated_doses, blm_types, f, ax, dcum_start, dcum_end, start, end = self.run_common_functions(blm_summing_func, blms)

        f.suptitle(r'Total integrated dose for [{} : {}] normalized with intensity: {:.2e} ps'.
                   format(start.strftime(self.date_format), end.strftime(self.date_format), integrated_intensity), fontsize=25)

        ax.set_ylabel(r'normalized TID [Gy/ps]', fontsize=12)

        self.__plot_blms(blm_positions, integrated_doses / integrated_intensity, blm_types, ax.semilogy)

        file_name = 'n_int_TID{}_{}_dcum_{}_{}'.format(start.strftime(self.date_format), end.strftime(self.date_format), int(dcum_start), int(dcum_end))
        file_path_name_without_extension = os.path.join(PLOT_DIR, file_name)
        self.save_plot_and_data(file_path_name_without_extension, blm_positions, integrated_doses / integrated_intensity)

    def plot_total_dose(self, blms, blm_summing_func):
        blm_positions, integrated_doses, blm_types, f, ax, dcum_start, dcum_end, start, end = self.run_common_functions(blm_summing_func, blms)

        f.suptitle(r'Total integrated dose for [{} : {}]'.format(start.strftime(self.date_format), end.strftime(self.date_format)), fontsize=25)

        ax.set_ylabel(r'TID [Gy]')

        self.__plot_blms(blm_positions, integrated_doses, blm_types, ax.semilogy)

        file_name = 'TID{}_{}_dcum_{}_{}'.format(start.strftime(self.date_format), end.strftime(self.date_format), int(dcum_start), int(dcum_end))
        file_path_name_without_extension = os.path.join(PLOT_DIR, file_name)
        self.save_plot_and_data(file_path_name_without_extension, blm_positions, integrated_doses)

    def plot_total_dose_extrapolated(self, blms, blm_summing_func):
        blm_positions, integrated_doses, blm_types, f, ax, dcum_start, dcum_end, start, end = self.run_common_functions(blm_summing_func, blms)

        f.suptitle(r'Extrapolated TID for HL LHC (3000 fb$^{{-1}}$) based on BLM data from {} until {} normalized with luminosity (44 fb^${{-1}}$)'.
                   format(start.strftime(self.date_format), end.strftime(self.date_format)), fontsize=25)

        ax.set_ylabel(r'Extrapolated TID [Gy]')

        self.__plot_blms(blm_positions, integrated_doses * 3000 / 44., blm_types, ax.semilogy)

        file_name = 'extrapolated_TID_{}_{}_dcum_{}_{}'.format(start.strftime(self.date_format), end.strftime(self.date_format), int(dcum_start), int(dcum_end))
        file_path_name_without_extension = os.path.join(PLOT_DIR, file_name)
        self.save_plot_and_data(file_path_name_without_extension, blm_positions, integrated_doses)

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

    def run_common_functions(self, blm_summing_func, blms):
        blm_positions, integrated_doses, blm_types = self.remove_nans(*self.get_sorted_blm_data(blms, blm_summing_func))
        start, end = self.get_plot_dates(blms)
        dcum_start, dcum_end = self.get_plot_xlim(blm_positions)
        f, ax = self.build_blm_layout(dcum_start, dcum_end)

        f.text(self.layout_plotter.start + .5 * self.layout_plotter.ran, 12,
                 'PRELIMINARY', fontsize=100, va='center', ha='center', color='gray', alpha=0.1, rotation=45)
        f.text(self.layout_plotter.start + .9 * self.layout_plotter.ran, -7,
                 'Courtesy MCWG: {}'.format(datetime.today().strftime('%Y-%m-%d %H:%M')), fontsize=12, va='bottom', ha='right', color='gray', alpha=0.5, rotation=0)
        ax.grid(True)
        ax.legend()
        return blm_positions, integrated_doses, blm_types, f,ax, dcum_start, dcum_end, start, end

    def remove_nans(self, blm_positions, integrated_doses, blm_types):
        integrated_doses_valid = np.logical_not(np.isnan(integrated_doses))
        return blm_positions[integrated_doses_valid], integrated_doses[integrated_doses_valid], blm_types[integrated_doses_valid]

    def get_plot_dates(self, blms):
        return datetime.utcfromtimestamp(blms[0].blm_intervals[0].start), datetime.utcfromtimestamp(blms[0].blm_intervals[-1].end)

    def get_plot_xlim(self, blm_positions):
        dcum_start = blm_positions[0] - (blm_positions[-1] - blm_positions[0]) * 0.01
        dcum_end = blm_positions[-1] + (blm_positions[-1] - blm_positions[0]) * 0.01
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

    def __plot_blms(self, blm_positions, integrated_doses, blm_types, func):
        func(blm_positions[blm_types == 1], integrated_doses[blm_types == 1], 'r.-', linewidth=0.1, markersize=10, label='Beam 1')
        func(blm_positions[blm_types == 2], integrated_doses[blm_types == 2], 'b.-', linewidth=0.1, markersize=10, label='Beam 2')
        func(blm_positions[blm_types == 0], integrated_doses[blm_types == 0], 'g.-', linewidth=0.1, markersize=10, label='Top BLMs')


if __name__ == '__main__':
    p = BLMsPlotter(None)
    p.plot(None)

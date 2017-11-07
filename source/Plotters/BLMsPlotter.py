import logging
import os
import re
from datetime import datetime
import config
import matplotlib.gridspec as gridspec
import matplotlib.dates as md
import matplotlib.colors as colors
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from projects.Plotting.python.plotting_layout import plotter_layout, PLOT_DIR

from source.BLM_dose_calculation_exceptions import NormalizedIntensityPlotRangeTooSmall, NormalizedLuminosityPlotRangeTooSmall
from source.Plotters.IPlotter import IPlotter
from config import LHC_LENGTH, INTENSITY_NORMALIZED_PLOT_YRANGE
from source.Plotters.schedule_plotter import schedule


class BLMsPlotter(IPlotter):
    """
    Tools to plot dose and normalized dose for specific blms.
    """
    regex_name_pattern = re.compile(r"([\w\.]+):(\w+)")
    date_format = '%Y%m%d'

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
        fig_size = [15, 15/1.618034]
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
        blm_positions, integrated_doses, blm_types, blm_names, f, ax, dcum_start, dcum_end, start, end = self.run_common_functions(blm_summing_func, blms)

        f.suptitle(r'Total integrated dose for [{} : {}] normalized with luminosity: {} fb${{^-1}}$'.
                   format(start.strftime(self.date_format), end.strftime(self.date_format), luminosity), fontsize=16, weight='bold')

        ax.set_ylabel(r'normalized TID [Gy/fb$^{-1}$]', fontsize=12)

        self.__plot_blms(blm_positions, integrated_doses / luminosity, blm_types, ax.semilogy)
        ax.legend()
        if self.check_luminosity_normalized_plot_range(integrated_doses / luminosity):
            ax.set_ylim(config.LUMINOSITY_NORMALIZED_PLOT_YRANGE)
        file_name = 'n_lum_TID{}_{}_{}'.format(start.strftime(self.date_format), end.strftime(self.date_format), self.get_fully_covered_lhc_section(dcum_start, dcum_end))
        file_path_name_without_extension = os.path.join(PLOT_DIR, file_name)
        self.save_plot_and_data(file_path_name_without_extension, blm_positions, integrated_doses / luminosity, blm_names)


    def plot_intensity_normalized_dose(self, blms, blm_summing_func, normalization_func):
        # it's sufficient to calculate normalization factor for one blm only, since intensity data are the same for all BLMs
        integrated_intensity = normalization_func(blms[0])
        logging.info('Calcualted intensity: ' + str(integrated_intensity))
        blm_positions, integrated_doses, blm_types, blm_names, f, ax, dcum_start, dcum_end, start, end = self.run_common_functions(blm_summing_func, blms)

        f.suptitle(r'Total integrated dose for [{} : {}] normalized with intensity: {:.2e} ps'.
                   format(start.strftime(self.date_format), end.strftime(self.date_format), integrated_intensity), fontsize=16, weight='bold')

        ax.set_ylabel(r'normalized TID [Gy/ps]', fontsize=12)
        self.__plot_blms(blm_positions, integrated_doses / integrated_intensity, blm_types, ax.semilogy)
        ax.legend()
        if self.check_intensity_normalized_plot_range(integrated_doses / integrated_intensity):
            ax.set_ylim(config.INTENSITY_NORMALIZED_PLOT_YRANGE)

        file_name = 'n_int_TID_{}_{}_{}'.format(start.strftime(self.date_format), end.strftime(self.date_format), self.get_fully_covered_lhc_section(dcum_start, dcum_end))
        file_path_name_without_extension = os.path.join(PLOT_DIR, file_name)
        self.save_plot_and_data(file_path_name_without_extension, blm_positions, integrated_doses / integrated_intensity, blm_names)
    def check_intensity_normalized_plot_range(self, normalized_doses):
        if np.max(normalized_doses) > config.INTENSITY_NORMALIZED_PLOT_YRANGE[1]:
            raise NormalizedIntensityPlotRangeTooSmall('There is at least one value ({}) higher than plot yrange.'.format(np.max(normalized_doses)))
        elif np.min(normalized_doses) < config.INTENSITY_NORMALIZED_PLOT_YRANGE[0]:
            raise NormalizedIntensityPlotRangeTooSmall('There is at least one value ({}) lower than plot yrange.'.format(np.min(normalized_doses)))
        else:
            return True

    def check_luminosity_normalized_plot_range(self, normalized_doses):
        if np.max(normalized_doses) > config.LUMINOSITY_NORMALIZED_PLOT_YRANGE[1]:
            raise NormalizedLuminosityPlotRangeTooSmall('There is at least one value ({}) higher than plot yrange.'.format(np.max(normalized_doses)))
        elif np.min(normalized_doses) < config.LUMINOSITY_NORMALIZED_PLOT_YRANGE[0]:
            raise NormalizedLuminosityPlotRangeTooSmall('There is at least one value ({}) lower than plot yrange.'.format(np.min(normalized_doses)))
        else:
            return True

    def plot_total_dose(self, blms, blm_summing_func):
        blm_positions, integrated_doses, blm_types, blm_names, f, ax, dcum_start, dcum_end, start, end = self.run_common_functions(blm_summing_func, blms)

        f.suptitle(r'Total integrated dose for [{} : {}]'.format(start.strftime(self.date_format), end.strftime(self.date_format)), fontsize=16, weight='bold')

        ax.set_ylabel(r'TID [Gy]')

        self.__plot_blms(blm_positions, integrated_doses, blm_types, ax.semilogy)
        ax.legend()
        file_name = 'TID_{}_{}_{}'.format(start.strftime(self.date_format), end.strftime(self.date_format), self.get_fully_covered_lhc_section(dcum_start, dcum_end))
        file_path_name_without_extension = os.path.join(PLOT_DIR, file_name)
        self.save_plot_and_data(file_path_name_without_extension, blm_positions, integrated_doses, blm_names)

    def plot_total_cumulated_dose(self, blms, blm_summing_func):
        f, ax = plt.subplots(1, 1, figsize=[15, 15/1.618034])
        xfmt = md.DateFormatter('%Y-%m-%d')
        ax.xaxis.set_major_formatter(xfmt)
        ax.xaxis_date()
        f.autofmt_xdate()
        plt.xlabel(r'Date')
        ax.grid(True)
        plt.ylabel(r'TID [Gy]')

        start_xaxis_date = None
        end_xaxis_date = None


        for blm in blms:
            blm_intervals_start = datetime.utcfromtimestamp(blm.blm_intervals[0].start)
            blm_intervals_end = datetime.utcfromtimestamp(blm.blm_intervals[-1].end)

            if start_xaxis_date is None and end_xaxis_date is None:
                start_xaxis_date = blm_intervals_start
                end_xaxis_date = blm_intervals_end
            elif start_xaxis_date > blm_intervals_start:
                start_xaxis_date = blm_intervals_start
            elif end_xaxis_date < blm_intervals_end:
                end_xaxis_date = blm_intervals_end

            dates = pd.date_range(blm_intervals_start, blm_intervals_end, freq='1D')
            num_of_days_between_start_and_end = len(dates)
            intensity = np.array([0] + [blm_summing_func(blm, dates[i], dates[i + 1]) for i in range(num_of_days_between_start_and_end - 1)])
            dates = pd.to_datetime(np.array((dates - datetime(1970, 1, 1)).total_seconds()), unit='s')
            plt.plot(dates, np.cumsum(intensity), label=blm.name)
        y_max = ax.get_ylim()
        sc = schedule(dates[0], dates[-1])
        ax.set_xlim(blm_intervals_start, blm_intervals_end)
        sc.schedule_plotter(ax)
        ax.set_ylim((0,y_max[1]))
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.16), fancybox=True, shadow=True, ncol=3)

        plt.title(r'Total ionizing dose - cumulative sum for [{} : {}]'.format(start_xaxis_date.strftime(self.date_format), end_xaxis_date.strftime(self.date_format)), fontsize=16, weight='bold')
        file_name = 'TID_cumsum_{}_{}'.format(start_xaxis_date.strftime(self.date_format), end_xaxis_date.strftime(self.date_format))
        file_path_name_without_extension = os.path.join(PLOT_DIR, file_name)

        self.save_plot(file_path_name_without_extension + '.png')
        self.save_plot(file_path_name_without_extension + '.pdf')


    def plot_total_dose_extrapolated(self, blms, blm_summing_func):
        blm_positions, integrated_doses, blm_types, blm_names, f, ax, dcum_start, dcum_end, start, end = self.run_common_functions(blm_summing_func, blms)

        f.suptitle(r'Extrapolated TID for HL LHC (3000 fb$^{{-1}}$) based on BLM data from {} until {} normalized with luminosity (44 fb^${{-1}}$)'.
                   format(start.strftime(self.date_format), end.strftime(self.date_format)), fontsize=25)

        ax.set_ylabel(r'Extrapolated TID [Gy]')

        self.__plot_blms(blm_positions, integrated_doses * 3000 / 44., blm_types, ax.semilogy)
        ax.legend()

        file_name = 'extrapolated_TID_{}_{}_{}'.format(start.strftime(self.date_format), end.strftime(self.date_format), self.get_fully_covered_lhc_section(dcum_start, dcum_end))
        file_path_name_without_extension = os.path.join(PLOT_DIR, file_name)
        self.save_plot_and_data(file_path_name_without_extension, blm_positions, integrated_doses, blm_names)

    def get_sorted_blm_data(self, blms, blm_summing_func):
        integrated_doses = np.zeros(len(blms), dtype=np.float)
        blm_positions = np.zeros(len(blms), dtype=np.float)
        blm_types = np.zeros(len(blms), dtype=np.float)
        blm_names = np.zeros(len(blms), dtype=np.dtype('a64'))
        for index, blm in enumerate(blms):
            integrated_doses[index] = blm_summing_func(blm)
            blm_positions[index] = blm.position
            blm_names[index] = blm.name
            blm_types[index] = self.get_blm_type(blm)
        if -1 in blm_types:
            raise Exception('Wrong recognized BLM type')
        order = blm_positions.argsort()
        return blm_positions[order], integrated_doses[order], blm_types[order], blm_names[order]

    def run_common_functions(self, blm_summing_func, blms):
        blm_positions, integrated_doses, blm_types, blm_names = self.remove_nans(*self.get_sorted_blm_data(blms, blm_summing_func))
        start, end = self.get_plot_dates(blms)
        dcum_start, dcum_end = self.get_plot_xlim(blm_positions)
        f, ax = self.build_blm_layout(dcum_start, dcum_end)

        f.text(self.layout_plotter.start + .5 * self.layout_plotter.ran, 12,
                 'PRELIMINARY', fontsize=100, va='center', ha='center', color='gray', alpha=0.1, rotation=45)
        f.text(self.layout_plotter.start + .9 * self.layout_plotter.ran, -7.5,
                 'Courtesy MCWG: {}'.format(datetime.today().strftime('%Y-%m-%d %H:%M')), fontsize=12, va='bottom', ha='right', color='gray', alpha=0.5, rotation=0)
        ax.grid(True)
        return blm_positions, integrated_doses, blm_types, blm_names, f,ax, dcum_start, dcum_end, start, end

    def remove_nans(self, blm_positions, integrated_doses, blm_types,blm_names):
        integrated_doses_valid = np.logical_not(np.isnan(integrated_doses))
        return blm_positions[integrated_doses_valid], integrated_doses[integrated_doses_valid], blm_types[integrated_doses_valid], blm_names[integrated_doses_valid]

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
        func(blm_positions[blm_types == 1], integrated_doses[blm_types == 1], 'r.-', linewidth=0.4, markersize=10, label='Beam 1')
        func(blm_positions[blm_types == 2], integrated_doses[blm_types == 2], 'b.-', linewidth=0.4, markersize=10, label='Beam 2')
        func(blm_positions[blm_types == 0], integrated_doses[blm_types == 0], 'g.-', linewidth=0.4, markersize=10, label='Top BLMs')


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
        xfmt = md.DateFormatter('%Y-%m-%d')
        ax.xaxis.set_major_formatter(xfmt)
        f.autofmt_xdate()
        plt.xlabel(r'date')
        plt.ylabel(r'position [m]')
        plt.pcolormesh(x, y, intens, label='dose', norm=colors.SymLogNorm(linthresh=0.03,vmin=intens.min(), vmax=intens.max()),  cmap='RdBu_r')
        plt.colorbar()
        self.legend()
        file_name = 'heatmap_TID_{}_{}{}'.format(x[0], x[-1], self.get_fully_covered_lhc_section(y[0], y[-1]))
        file_path_name_without_extension = os.path.join(PLOT_DIR, file_name)
        self.save_plot(file_path_name_without_extension)




if __name__ == '__main__':
    p = BLMsPlotter(None)
    print(p.get_fully_covered_lhc_section(26658,26658))

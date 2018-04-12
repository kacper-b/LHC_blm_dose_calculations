import logging
import os
import re
from datetime import datetime
import config
from config import BEAM_MODES
from tools.workers import second2datetime
import matplotlib
matplotlib.use('agg') 
import matplotlib.gridspec as gridspec
import matplotlib.dates as md
import matplotlib.colors as colors
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from Plotting.python.plotting_layout import plotter_layout
from source.BLM_dose_calculation_exceptions import NormalizedIntensityPlotRangeTooSmall, NormalizedLuminosityPlotRangeTooSmall
from source.Plotters.IPlotter import IPlotter
from source.Plotters.schedule_plotter import schedule
import seaborn as sns

ir1 = ['BLMQI.13L1.B2E30_MQ', 'BLMEI.11L1.B2E30_LEFL', 'BLMQI.09L1.B2E10_MQM', 'BLMTI.06L1.B2E10_TCL.6L1.B2', 'BLMTI.04L1.B2E10_TANAL.4L1',
       'BLMQI.03L1.B2E30_MQXA', 'BLMQI.03R1.B1E30_MQXA', 'BLMTI.04R1.B1E10_TANAR.4R1', 'BLMTI.06R1.B1E10_TCL.6R1.B1', 'BLMQI.09R1.B1E10_MQM',
       'BLMEI.11R1.B1E21_LEHR', 'BLMQI.13R1.B1E10_MQ']

ir2 = ["BLMQI.08L2.B1E30_MQML", "BLMQI.06L2.B1E20_MQML", "BLMTI.04L2.B1E20_TDI.4L2.B1", "BLMEI.01L2.B1E10_MBWMD", "BLMTI.04R2.B1I10_TCLIA.4R2",
       "BLMTI.04R2.B2E10_TCTPV.4R2.B2", "BLMTI.06R2.B1I10_TCLIB.6R2.B1", "BLMQI.09R2.B1I10_MQM"]

ir3 = ["BLMQI.12L3.B1I10_MQ", "BLMQI.09L3.B2E10_MQ", "BLMTI.07L3.B2E10_TCLA.7L3.B2", "BLMTI.06L3.B1I10_TCAPA.6L3.B1", "BLMEI.05L3.B1I10_TCSM.5L3.B1",
       "BLMTI.05L3.B2E10_TCLA.B5L3.B2", "BLMEI.05L3.B2E10_TCSM.B5L3.B2", "BLMEI.05R3.B1I10_TCSM.B5R3.B1", "BLMTI.05R3.B1I10_TCLA.B5R3.B1",
       "BLMEI.05R3.B2E10_TCSM.5R3.B2", "BLMTI.06R3.B2E10_TCAPA.6R3.B2", "BLMTI.07R3.B1I10_TCLA.7R3.B1", "BLMQI.08R3.B1I10_MQ", "BLMQI.11R3.B1I10_MQ"]

ir4 = ["BLMQI.07L4.B2E10_MQM", "BLMQI.06L4.B2E10_MQY", "BLMEI.05L4.B2E10_BSRTM", "BLMEI.05R4.B1I10_BSRTM", "BLMQI.05R4.B1I30_MQY", "BLMQI.07R4.B1I10_MQM",
       "BLMQI.11R4.B2E30_MQ"]

ir5 = ['BLMQI.13L5.B2E10_MQ', 'BLMEI.11L5.B2E22_LEFL', 'BLMQI.09L5.B2E10_MQM', 'BLMTI.06L5.B2E10_TCL.6L5.B2', 'BLMTI.04L5.B2E10_TANC.4L5',
       'BLMTI.04R5.B1E10_TANC.4R5', 'BLMTI.06R5.B1E10_TCL.6R5.B1', 'BLMQI.09R5.B1E10_MQM', 'BLMQI.11R5.B1E10_MQ', 'BLMQI.13R5.B1E10_MQ']

ir6 = ["BLMQI.09L6.B2I30_MQM", "BLMQI.04L6.B2I30_MQY", "BLMTI.04L6.B2I11_TCSP.A4L6.B2", "BLMTI.04L6.B1E10_TCDSA.4L6.B1", "BLMTI.04R6.B2I10_TCDSA.4R6.B2",
       "BLMTI.04R6.B1E10_TCSP.A4R6.B1", "BLMQI.04R6.B1E30_MQY", "BLMQI.10R6.B1E10_MQML",]

ir7 = ["BLMQI.08L7.B2I30_MQ", "BLMEI.06L7.B1E10_TCP.A6L7.B1", "BLMTI.06L7.B2I10_TCLA.A6L7.B2", "BLMEI.05L7.B1E10_TCSM.A5L7.B1", "BLMEI.04L7.B1E10_TCSM.A4L7.B1",
       "BLMEI.04R7.B1E10_TCSM.A4R7.B1", "BLMEI.05R7.B2I10_TCSM.B5R7.B2", "BLMTI.06R7.B1E10_TCLA.A6R7.B1", "BLMEI.06R7.B2I10_TCHSV.6R7.B2", "BLMQI.08R7.B1E30_MQ",]

ir8 = ["BLMQI.09L8.B2I30_MQM", "BLMQI.08L8.B2I10_MQML", "BLMTI.06L8.B2I10_TCLIB.6L8.B2", "BLMQI.05L8.B2I30_MQM", "BLMTI.04L8.B1E10_TCTPV.4L8.B1",
       "BLMQI.01L8.B1E30_MQXA", "BLMQI.01R8.B2E30_MQXA", "BLMTI.04R8.B2E10_TCTPV.4R8.B2", "BLMQI.05R8.B1I30_MQY", "BLMQI.06R8.B1I10_MQML",
       "BLMQI.08R8.B1I10_MQML", "BLMQI.09R8.B1I30_MQM"]

BLMs_to_be_annotated = ir1 + ir2 + ir3 + ir4 + ir5 + ir6 + ir7 + ir8

class BLMsPlotter(IPlotter):
    """
    Tools to plot dose and normalized dose for specific blms.
    """
    date_format = '%Y%m%d'
    title_date_format = '%Y-%m-%d'


    def __init__(self, output_directory, blm_csv_list_filename, start=None, end=None):
        """
        :param str output_directory: plots output directory
        """
        self.plot_directory = output_directory
        self.layout_plotter = plotter_layout()
        self.blm_csv_list_filename = blm_csv_list_filename
        self.start = start
        self.end = end

    def build_blm_layout(self, dcum_start, dcum_end):
        """
        It plots LHC layout (BLM and optionally optics)
        :param float dcum_start: in meters
        :param dcum_end:in meters
        :return tuple: plt, ax (see matplotlib naming convention)
        """
        matplotlib.style.use('ggplot')
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
        """
        The functions plots dose normalised with integrated luminosity (logscale), then saves plot and plot's data.
        :param list blms: BLM list
        :param lambda blm_summing_func: a function which takes blm as an argument and returns integrated dose for that blm
        :param float luminosity: integrated luminosity (for the analyzed time period)
        :return:
        """
        blm_positions, integrated_doses, blm_types, blm_names, f, ax, dcum_start, dcum_end, start, end = self.run_common_functions(blm_summing_func, blms)

        f.suptitle(r'Total integrated dose for [{} : {}] normalized with luminosity: {} fb${{^-1}}$'.
                   format(start.strftime(self.title_date_format), end.strftime(self.title_date_format), luminosity), fontsize=16, weight='bold')

        ax.set_ylabel(r'normalized TID (Gy/fb$^{-1}$)', fontsize=12)

        self.__plot_blms(blm_positions, integrated_doses / luminosity, blm_types, ax.semilogy)
        ax.legend()
        if self.check_luminosity_normalized_plot_range(integrated_doses / luminosity):
            ax.set_ylim(config.LUMINOSITY_NORMALIZED_PLOT_YRANGE)
        file_name = 'n_lum_TID{}_{}_{}'.format(start.strftime(self.date_format), end.strftime(self.date_format), self.get_fully_covered_lhc_section(dcum_start, dcum_end))
        file_path_name_without_extension = os.path.join(self.plot_directory, file_name)
        self.save_plot_and_data(file_path_name_without_extension, blm_positions, integrated_doses / luminosity, blm_names)

    def plot_luminosity_normalized_dose_for_multiple_years(self, lum_blms, blm_summing_func):
        blm_positions, integrated_doses, blm_types, blm_names = self.remove_nans(*self.get_sorted_blm_data(list(lum_blms.values())[0], blm_summing_func))
        # print(lum_blms)
        dcum_start, dcum_end = self.get_plot_xlim(blm_positions)
        plt, ax = self.build_blm_layout(dcum_start, dcum_end)
        plt.text(self.layout_plotter.start + .9 * self.layout_plotter.ran, -7.5,
                 'Courtesy MCWG: {}'.format(datetime.today().strftime('%Y-%m-%d %H:%M')), fontsize=12, va='bottom', ha='right', color='gray', alpha=0.5,
                 rotation=0)
        ax.grid(True)

        ax.set_ylabel(r'normalized TID (Gy/fb$^{-1}$)', fontsize=12)
        self.add_dashed_lines(ax, BLMs_to_be_annotated, blm_names, blm_positions, integrated_doses)
        for luminosity, blms in lum_blms.items():
            blm_positions, integrated_doses, blm_types, blm_names = self.remove_nans(*self.get_sorted_blm_data(blms, blm_summing_func))
            start, end = self.get_plot_dates(blms)
            ax.semilogy(blm_positions, integrated_doses / luminosity, label=r'TID for [{} : {}] normalized with luminosity: {} fb${{^-1}}$'.
                   format(start.strftime(self.title_date_format), end.strftime(self.title_date_format), luminosity))
        ax.legend(framealpha=1)
        # if self.check_luminosity_normalized_plot_range(integrated_doses / luminosity):
        ax.set_ylim((1e-4, 1e4))
        file_name = 'n_lum_TID_multip_{}'.format(self.get_fully_covered_lhc_section(dcum_start, dcum_end))
        file_path_name_without_extension = os.path.join(self.plot_directory, file_name)
        self.save_plot(file_path_name_without_extension + '.png')
        self.save_plot(file_path_name_without_extension + '.pdf')

        # self.save_plot_and_data(file_path_name_without_extension, blm_positions, integrated_doses / luminosity, blm_names)

    def plot_intensity_normalized_dose(self, blms, blm_summing_func, normalization_func):
        """
        The functions plots dose normalised with integrated intensity (logscale), then saves plot and plot's data.
        :param list blms: BLM list
        :param lambda blm_summing_func: a function which takes blm as an argument and returns integrated dose for that blm
        :param normalization_func: a function which takes blm as an argument and returns integrated intensity
        :return:
        """
        # it's sufficient to calculate normalization factor for one blm only, since intensity data are the same for all BLMs
        integrated_intensity = normalization_func(blms[0])
        logging.info('Calcualted intensity: ' + str(integrated_intensity))
        blm_positions, integrated_doses, blm_types, blm_names, f, ax, dcum_start, dcum_end, start, end = self.run_common_functions(blm_summing_func, blms)

        f.suptitle(r'Total integrated dose for [{} : {}] normalized with intensity: {:.2e} ps'.
                   format(start.strftime(self.title_date_format), end.strftime(self.title_date_format), integrated_intensity), fontsize=16, weight='bold')

        ax.set_ylabel(r'normalized TID (Gy/ps)', fontsize=12)
        self.__plot_blms(blm_positions, integrated_doses / integrated_intensity, blm_types, ax.semilogy)
        ax.legend()
        if self.check_intensity_normalized_plot_range(integrated_doses / integrated_intensity):
            ax.set_ylim(config.INTENSITY_NORMALIZED_PLOT_YRANGE)

        file_name = 'n_int_TID_{}_{}_{}'.format(start.strftime(self.date_format), end.strftime(self.date_format), self.get_fully_covered_lhc_section(dcum_start, dcum_end))
        file_path_name_without_extension = os.path.join(self.plot_directory, file_name)
        self.save_plot_and_data(file_path_name_without_extension, blm_positions, integrated_doses / integrated_intensity, blm_names)

    def check_intensity_normalized_plot_range(self, normalized_doses):
        """
        It checks if all the data are in the range specified by INTENSITY_NORMALIZED_PLOT_YRANGE. If no, it throws an exception NormalizedIntensityPlotRangeTooSmall
        :param normalized_doses:
        :return:
        """
        if np.max(normalized_doses) > config.INTENSITY_NORMALIZED_PLOT_YRANGE[1]:
            raise NormalizedIntensityPlotRangeTooSmall('There is at least one value ({}) higher than plot yrange.'.format(np.max(normalized_doses)))
        elif np.min(normalized_doses) < config.INTENSITY_NORMALIZED_PLOT_YRANGE[0]:
            raise NormalizedIntensityPlotRangeTooSmall('There is at least one value ({}) lower than plot yrange.'.format(np.min(normalized_doses)))
        else:
            return True

    def check_luminosity_normalized_plot_range(self, normalized_doses):
        """
        It checks if all the data are in the range specified by LUMINOSITY_NORMALIZED_PLOT_YRANGE. If no, it throws an exception NormalizedLuminosityPlotRangeTooSmall
        :param normalized_doses:
        :return:
        """
        if np.max(normalized_doses) > config.LUMINOSITY_NORMALIZED_PLOT_YRANGE[1]:
            raise NormalizedLuminosityPlotRangeTooSmall('There is at least one value ({}) higher than plot yrange.'.format(np.max(normalized_doses)))
        elif np.min(normalized_doses) < config.LUMINOSITY_NORMALIZED_PLOT_YRANGE[0]:
            raise NormalizedLuminosityPlotRangeTooSmall('There is at least one value ({}) lower than plot yrange.'.format(np.min(normalized_doses)))
        else:
            return True

    def add_annotations(self, ax, annotated_blm_names, blm_names, blm_positions, integrated_doses):
        """

        :param ax:
        :param annotated_blm_names:
        :param blm_names:
        :param blm_positions:
        :param integrated_doses:
        :return:
        """
        counter = 0
        for index, blm_name in enumerate(blm_names):
            if blm_name in annotated_blm_names:
                counter += 1
                print(blm_name, counter, blm_positions[index], integrated_doses[index])
                ax.annotate(counter, (blm_positions[index], integrated_doses[index]), (0, 20), textcoords='offset points',
                            arrowprops=dict(arrowstyle='-', linestyle="dashed", color="0"))
    def add_dashed_lines(self, ax, annotated_blm_names, blm_names, blm_positions, integrated_doses):
        """

        :param ax:
        :param annotated_blm_names:
        :param blm_names:
        :param blm_positions:
        :param integrated_doses:
        :return:
        """
        counter = 0
        for index, blm_name in enumerate(blm_names):
            if blm_name in annotated_blm_names:
                counter += 1
                ax.axvline(x=blm_positions[index],ymax=0.94, linewidth=1, color='#babdb6', ls='dashed')
                ax.text(blm_positions[index], 5e3,  str(counter), horizontalalignment='center', rotation=0)

                print(blm_name, counter, blm_positions[index])
                # ax.annotate(counter, (blm_positions[index], integrated_doses[index]), (0, 20), textcoords='offset points',
                #             arrowprops=dict(arrowstyle='-', linestyle="dashed", color="0"))


    def plot_total_dose(self, blms, blm_summing_func):
        """
        The functions plots dose (logscale), then saves plot and plot's data.
        :param list blms: BLM list
        :param lambda blm_summing_func: a function which takes blm as an argument and returns integrated dose for that blm
        :param normalization_func: a function which takes blm as an argument and returns integrated intensity
        :return:
        """
        blm_positions, integrated_doses, blm_types, blm_names, f, ax, dcum_start, dcum_end, start, end = self.run_common_functions(blm_summing_func, blms)

        # f.suptitle(r'Total integrated dose for [{} : {}]'.format(start.strftime(self.title_date_format), end.strftime(self.title_date_format)), fontsize=16, weight='bold')

        ax.set_ylabel(r'TID (Gy)')

        self.__plot_blms(blm_positions, integrated_doses, blm_types, ax.semilogy)

        #self.add_annotations(ax, BLMs_to_be_annotated, blm_names, blm_positions, integrated_doses)

        ax.legend()
        #ax.set_ylim((5e-3,1e6))
        # file_name = 'TID_{}_{}_{}'.format(start.strftime(self.date_format), end.strftime(self.date_format), self.get_fully_covered_lhc_section(dcum_start, dcum_end))
        if self.start and self.end:
            start = self.start
            end = self.end
        file_name = 'TID_{}_{}_{}'.format(start.strftime(self.date_format), end.strftime(self.date_format),self.blm_csv_list_filename)

        file_path_name_without_extension = os.path.join(self.plot_directory, file_name)
        self.save_plot_and_data(file_path_name_without_extension, blm_positions, integrated_doses, blm_names)

    def plot_total_cumulated_dose(self, blms, blm_summing_func):
        """
        The functions plots cumulated dose for given BLMs with the LHC schedule, then saves plot and plot's data.
        :param list blms: BLM list
        :param lambda blm_summing_func: a function which takes blm as an argument and returns integrated dose for that blm
        :return:
        """

        # Plot parameters
        f, ax = plt.subplots(1, 1, figsize=[15, 15/1.618034])
        xfmt = md.DateFormatter('%Y-%m-%d')
        ax.xaxis.set_major_formatter(xfmt)
        ax.xaxis_date()
        f.autofmt_xdate()
        plt.xlabel(r'Date')
        plt.ylabel(r'TID (Gy)')

        # variables which will store the earliest and latest date of analysed blms data
        start_xaxis_date = None
        end_xaxis_date = None
        # colors = sns.color_palette("Set2", len(blms))
        matplotlib.rcParams['axes.prop_cycle']  = matplotlib.cycler(color=sns.color_palette("hls", 15))

        positions = []
        for blm in blms:
            blm_intervals_start = second2datetime(blm.blm_intervals[0].start)
            blm_intervals_end = second2datetime(blm.blm_intervals[-1].end)
            positions.append(blm.position)

            if start_xaxis_date is None and end_xaxis_date is None:
                start_xaxis_date = blm_intervals_start
                end_xaxis_date = blm_intervals_end
            if start_xaxis_date > blm_intervals_start:
                start_xaxis_date = blm_intervals_start
            if end_xaxis_date < blm_intervals_end:
                end_xaxis_date = blm_intervals_end

            # divide plot range by days
            # st = datetime(blm_intervals_start.year, blm_intervals_start.month, blm_intervals_start.day)
            # en = datetime(blm_intervals_end.year, blm_intervals_end.month, blm_intervals_end.day)
            dates = pd.date_range(blm_intervals_start, blm_intervals_end, freq='1D')
            num_of_days_between_start_and_end = len(dates)
            # integrate over one day periods
            intensity = np.array([0] + [blm_summing_func(blm, dates[i], dates[i + 1]) for i in range(num_of_days_between_start_and_end - 1)])
            dates = pd.to_datetime(np.array((dates - datetime(1970, 1, 1)).total_seconds()), unit='s')
            plt.plot(dates, np.cumsum(intensity), label=blm.name)
            print(blm.name, sum(intensity), sep=2*'\t')
        y_max = ax.get_ylim()
        # Plot the LHC schedule
        sc = schedule(dates[0].year)
        ax.set_xlim(blm_intervals_start, blm_intervals_end)
        sc.schedule_plotter(ax, blm_intervals_start, blm_intervals_end)
        ax.grid(True)
        # ax.set_axisbelow(True)
        # ax.yaxis.grid(color='black', linestyle='dashed')
        # set plot parameters
        ax.set_ylim((0,y_max[1]))

        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.14), fancybox=True, shadow=True, ncol=5)

        plt.title(r'Total ionizing dose - cumulative sum for [{} : {}]'.format(start_xaxis_date.strftime(self.title_date_format),
                                                                               end_xaxis_date.strftime(self.title_date_format)), fontsize=16, weight='bold')
        file_name = 'TID_cumsum_{}_{}_dcum-range_{}_{}'.format(start_xaxis_date.strftime(self.date_format), end_xaxis_date.strftime(self.date_format), int(min(positions)), int(max(positions)))
        file_path_name_without_extension = os.path.join(self.plot_directory, file_name)

        self.save_plot(file_path_name_without_extension + '.png')
        self.save_plot(file_path_name_without_extension + '.pdf')

    def get_sorted_blm_data(self, blms, blm_summing_func):
        """
        It provides a sorted (by the dcum) data.
        :param list blms: BLM list
        :param lambda blm_summing_func: a function which takes blm as an argument and returns integrated dose for that blm
        :return tuple: blm_dcums, integrated_doses, blm_types, blm_names
        """
        integrated_doses = np.zeros(len(blms), dtype=np.float)
        blm_positions = np.zeros(len(blms), dtype=np.float)
        blm_types = np.zeros(len(blms), dtype=np.float)
        blm_names = np.zeros(len(blms), dtype=np.dtype('a64')).astype(str)
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
        """
        It runs common functions: sums integrated doses, removes nans, gets plot xrange, plots layout and adds 'Courtesy MCWG' & 'PRELIMINARY' watermarks.
        :param lambda blm_summing_func: a function which takes blm as an argument and returns integrated dose for that blm
        :param list blms: BLM list
        :return tuple: blm_positions, integrated_doses, blm_types, blm_names, plt,ax, dcum_start, dcum_end, start, end
        """
        blm_positions, integrated_doses, blm_types, blm_names = self.remove_nans(*self.get_sorted_blm_data(blms, blm_summing_func))
        start, end = self.get_plot_dates(blms)
        dcum_start, dcum_end = self.get_plot_xlim(blm_positions)
        plt, ax = self.build_blm_layout(dcum_start, dcum_end)

        # plt.text(self.layout_plotter.start + .5 * self.layout_plotter.ran, 12,
        #          'PRELIMINARY', fontsize=100, va='center', ha='center', color='gray', alpha=0.1, rotation=45)
        plt.text(self.layout_plotter.start + .9 * self.layout_plotter.ran, -7.5,
                 'Courtesy MCWG: {}'.format(datetime.today().strftime('%Y-%m-%d %H:%M')), fontsize=12, va='bottom', ha='right', color='gray', alpha=0.5, rotation=0)
        ax.grid(True)
        return blm_positions, integrated_doses, blm_types, blm_names, plt,ax, dcum_start, dcum_end, start, end

    def remove_nans(self, blm_positions, integrated_doses, blm_types,blm_names):
        """
        It removes Nan from integrated dose's array
        :param numpy.array blm_positions:
        :param numpy.array integrated_doses:
        :param numpy.array blm_types:
        :param numpy.array blm_names:
        :return:
        """
        integrated_doses_valid = np.logical_not(np.isnan(integrated_doses))
        return blm_positions[integrated_doses_valid], integrated_doses[integrated_doses_valid], blm_types[integrated_doses_valid], blm_names[integrated_doses_valid]

    def get_plot_dates(self, blms):
        """
        It returns the plot time range.
        :param list blms: sorted by date BLM list
        :return tuple: first and last timestamp in the first BLM from the BLM list - blms.
        """
        return second2datetime(blms[0].blm_intervals[0].start), second2datetime(blms[0].blm_intervals[-1].end)

    def get_plot_xlim(self, blm_positions):
        """
        It returns a plot x-axis range.
        :param numpy.array blm_positions:
        :return tuple:
        """
        dcum_start = blm_positions[0] - (blm_positions[-1] - blm_positions[0]) * 0.01
        dcum_end = blm_positions[-1] + (blm_positions[-1] - blm_positions[0]) * 0.01
        return dcum_start, dcum_end

    def get_plot_file_name(self, blm):
        """
        It returns blm name in a format, which can be used in a file name.
        :param blm:
        :return str:
        """
        return blm.get_file_name()

    def remove_field_name(self, blm_timber_query):
        """
        It removes everything after a colon.
        :param blm_timber_query:
        :return:
        """
        blm_timber_query_splitted = blm_timber_query.split(':')
        if len(blm_timber_query_splitted) == 2:
            return blm_timber_query_splitted[0]
        else:
            return blm_timber_query

    def get_blm_type(self, blm):
        """
        It returns beam which is related to the given blm.
        :param BLM blm: a BLM class object which has name property
        :return str: B1, B2 or B0
        """
        blm_type = -1
        if '.B0' in blm.name:
            blm_type = 0
        elif '.B1' in blm.name:
            blm_type = 1
        elif '.B2' in blm.name:
            blm_type = 2
        return blm_type

    def __plot_blms(self, blm_positions, integrated_doses, blm_types, func):
        """
        Plots BLM data, for each beam separately.
        :param blm_positions: list of BLM dcums
        :param integrated_doses: list of integrated BLM doses
        :param blm_types: list of blm types
        :param func: plotting function - ex. ax.plot
        :return:
        """
        func(blm_positions[blm_types == 1], integrated_doses[blm_types == 1], 'r.-', linewidth=0.4, markersize=10, label='Beam 1')
        func(blm_positions[blm_types == 2], integrated_doses[blm_types == 2], 'b.-', linewidth=0.4, markersize=10, label='Beam 2')
        # func(blm_positions[blm_types == 0], integrated_doses[blm_types == 0], 'g.-', linewidth=0.4, markersize=10, label='Top BLMs')
        func(blm_positions[blm_types == 0], integrated_doses[blm_types == 0], 'g.', markersize=10, label='Top BLMs')


    def heat_map_plot(self, blms):
        # TODO: to be removed or finished + commented
        dates = pd.date_range(second2datetime(blms[0].blm_intervals[0].start), second2datetime(blms[0].blm_intervals[-1].end), freq='1D')
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
        plt.ylabel(r'position (m)')
        plt.pcolormesh(x, y, intens, label='dose', norm=colors.SymLogNorm(linthresh=0.03,vmin=intens.min(), vmax=intens.max()),  cmap='RdBu_r')
        plt.colorbar()
        self.legend()
        file_name = 'heatmap_TID_{}_{}{}'.format(x[0], x[-1], self.get_fully_covered_lhc_section(y[0], y[-1]))
        file_path_name_without_extension = os.path.join(self.plot_directory, file_name)
        self.save_plot(file_path_name_without_extension)

    def plot_total_dose_extrapolated(self, blms, blm_summing_func):
        # TODO: to be removed or commented
        # That function won't be in the future

        blm_positions, integrated_doses, blm_types, blm_names, f, ax, dcum_start, dcum_end, start, end = self.run_common_functions(blm_summing_func, blms)

        f.suptitle(r'Extrapolated TID for HL LHC (3000 fb$^{{-1}}$) based on BLM data from {} until {} normalized with luminosity (44 fb^${{-1}}$)'.
                   format(start.strftime(self.title_date_format), end.strftime(self.title_date_format)), fontsize=25)

        ax.set_ylabel(r'Extrapolated TID (Gy)')

        self.__plot_blms(blm_positions, integrated_doses * 3000 / 44., blm_types, ax.semilogy)
        ax.legend()

        file_name = 'extrapolated_TID_{}_{}_{}'.format(start.strftime(self.date_format), end.strftime(self.date_format), self.get_fully_covered_lhc_section(dcum_start, dcum_end))
        file_path_name_without_extension = os.path.join(self.plot_directory, file_name)
        self.save_plot_and_data(file_path_name_without_extension, blm_positions, integrated_doses, blm_names)

    def plot_beam_modes(self, blm):
        # TODO: to be removed or commented

        # Pie chart, where the slices will be ordered and plotted counter-clockwise:
        beam_modes = list(BEAM_MODES.keys())
        labels = list(map(str,beam_modes))
        norm = 1 / blm.get_pre_oc_dose()
        sizes = {beam_mode:blm.get_pre_oc_dose_for_beam_mode([beam_mode])*norm for beam_mode in beam_modes}
        print(blm.name, sizes)
        explode = (0.1, 0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')
        # explode=explode
        # fig1, ax1 = plt.subplots()
        # # print(sizes)
        # items = list(sizes.items())
        # labels = [str(beam_mode) for beam_mode, val in items if val > 0.01]
        # ax1.pie([val for beam_mode, val in items if val > 0.005], labels=labels, explode=len(labels)*[0.2], autopct='%1.1f%%',
        #         shadow=False, startangle=90)
        # ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        #
        # plt.show()


if __name__ == '__main__':
    p = BLMsPlotter(None)
    print(p.get_fully_covered_lhc_section(26658,26658))

import pandas as pd
import numpy as np
import os
import sys,re
import pickle
import random
import time
from decimal import Decimal
from datetime import datetime, timedelta
from statsmodels.nonparametric.smoothers_lowess import lowess
from DosesCalculationReader import DosesCalculationReader
from config import DATA_DIRs_NAMES, PICKLE_INTENSITY_INTERVALS_PATH
from BLM_dose_calculation_exceptions import *
from multiprocessing import Pool


import glob

class IntensityIntervalsLoader:
    """

    """
    def __init__(self):
        """

        """
        self.regex = r".*_(\d{8})\d*_(\d{8})\d*\.p"
        self.file_paths = []
        self.intensity_intervals = []

    def set_files_paths(self, directory, start, end):
        """

        :param directory:
        :param start:
        :param end:
        :return:
        """
        for filename in glob.iglob(os.path.join(directory,'**/*'), recursive=True):
            start_end_date = re.match(self.regex, filename)
            if start_end_date:
                start_file_date = datetime.strptime(start_end_date.group(1), '%Y%m%d')
                end_file_date = datetime.strptime(start_end_date.group(2), '%Y%m%d')
                is_between = (start <= start_file_date and end_file_date <= end)
                is_end_covers = start_file_date <= end <= end_file_date
                is_beginning_covers = start_file_date <= start <= end_file_date
                if is_between or is_end_covers or is_beginning_covers:
                    self.file_paths.append(filename)

    def read_pickled_intensity_intervals(self):
        """

        :param fix_imports:
        :return:
        """
        import projects.LHC_intensity_calculations.source
        sys.modules['source'] = projects.LHC_intensity_calculations.source
        for file_path in self.file_paths:
            with open(file_path, 'rb') as interval_pickle:
                self.intensity_intervals.extend(pickle.load(interval_pickle))

    def filter_interval_by_dates(self, start_date, end_date):
        start_in_sec = (start_date - datetime.utcfromtimestamp(0)).total_seconds()
        end_in_sec = (end_date - datetime.utcfromtimestamp(0)).total_seconds()
        func = (lambda interval: start_in_sec <= interval.start and interval.end <= end_in_sec)
        self.intensity_intervals = list(filter(func, self.intensity_intervals))


class BLMLoader:
    """

    """
    def __init__(self):
        """

        """
        self.regex = r".*_(\d{4}(?:_?)\d{2}(?:_?)\d{2})\d*_(\d{4}(?:_?)\d{2}(?:_?)\d{2})\d*.*\.p"
        self.file_paths = []
        self.blm_data = []

    def set_files_paths(self, directory, start, end):
        """

        :param directory:
        :param start:
        :param end:
        :return:
        """
        for filename in glob.iglob(os.path.join(directory,'**/*'), recursive=True):
            start_end_date = re.match(self.regex, filename)
            if start_end_date:
                dt = timedelta(milliseconds=1)
                start_file_date = datetime.strptime(start_end_date.group(1), '%Y_%m_%d')
                end_file_date = datetime.strptime(start_end_date.group(2), '%Y_%m_%d')
                is_between = (start - dt <= start_file_date and end_file_date <= end + dt)
                is_end_covers = start_file_date < end < end_file_date + dt
                is_beginning_covers = start_file_date - dt < start < end_file_date
                if is_between or is_end_covers or is_beginning_covers:
                    self.file_paths.append(filename)

    def read_pickled_blms(self):
        """

        :param fix_imports:
        :return:
        """
        for file_path in self.file_paths:
            with open(file_path, 'rb') as interval_pickle:
                self.blm_data.append(pickle.load(interval_pickle))

    def group_by_blm_name(self):
        tmp = {}
        for blm in self.blm_data:
            if len(blm.columns) != 1:
                raise ValueError('Data from BLM should have only one column!')
            tmp[blm.columns[0]] = tmp.setdefault(blm.columns[0], pd.DataFrame()).append(blm)
        for blm in tmp.values():
            blm.sort_index(inplace=True)
        return tmp

    def get_blms(self):
        return (BLMDoseCalc(key, data) for key,data in self.group_by_blm_name().items())


class BLMDoseCalc:
    def __init__(self, name, data):
        self.name = name
        self.data = data

    def integrate_over_intensity_interval(self, intensity_interval):
        integration_result = 0
        offset = 0
        try:
            integration_result = self.__integrate(intensity_interval)
            offset = self.offset_calc_post(intensity_interval)
        except (IntegrationError_IntegrationResultBelowZero, IntegrationError_IIntervalNotCoveredByBLMData,
                IntegrationError_NoBLMDataForIInterval, PreOffsetEmpty, PostOffsetNan, PreOffsetNan,
                PostOffsetEmpty, PreOffsetBelowZero, PostOffsetBelowZero) as e:
            # print(e)
            pass
        return integration_result - offset * (intensity_interval.end - intensity_interval.start)

    def __integrate(self, intensity_interval):
        beam_period = (intensity_interval.start <= self.data.index) & (self.data.index <= intensity_interval.end)
        is_whole_period_covered_by_data = (intensity_interval.start >= self.data.index[0]) & (self.data.index[-1] >= intensity_interval.end)

        if not self.data[beam_period].empty and is_whole_period_covered_by_data:
            integral = np.trapz(y=self.data[beam_period][self.data.columns[0]], x=self.data[beam_period].index)
            if integral < 0:
                raise IntegrationError_IntegrationResultBelowZero('{} integrated dose < 0: {}'.format(self.name, intensity_interval))
            return integral

        elif not is_whole_period_covered_by_data:
            raise IntegrationError_IIntervalNotCoveredByBLMData('intensity interval does not cover {}: {}'.format(self.name, intensity_interval))
        else:
            raise IntegrationError_NoBLMDataForIInterval('{} dataframe for given intensity interval is empty: {}'.format(self.name, intensity_interval))

    def offset_calc_pre(self, intensity_interval, offset_sec=5 * 60):
        offset_period = (self.data.index >= (intensity_interval.start - offset_sec)) & (self.data.index <= intensity_interval.start)
        offset_interval_pre = self.data[offset_period]

        if not offset_interval_pre.empty:
            offset = np.mean(offset_interval_pre[self.name])
            if ~np.isnan(offset):
                if offset < 0:
                    raise PreOffsetBelowZero('{} pre-offset dataframe is empty: {}'.format(self.name, intensity_interval))
                return offset
            else:
                raise PreOffsetNan('{} pre-offset dataframe is empty: {}'.format(self.name, intensity_interval))
        else:
            raise PreOffsetEmpty('{} pre-offset dataframe is empty: {}'.format(self.name, intensity_interval))

    def offset_calc_post(self, intensity_interval, offset_sec=5 * 60):
        offset_period = (self.data.index >= intensity_interval.end) & (self.data.index <= intensity_interval.end + offset_sec)
        offset_interval_post = self.data[offset_period]

        if not offset_interval_post.empty:
            offset = np.mean(offset_interval_post[self.name])
            if not np.isnan(offset):
                if offset < 0:
                    raise PostOffsetBelowZero('Post-offset value is < 0: {} {}'.format(self.name, intensity_interval))
                return offset
            else:
                raise PostOffsetNan('Post-offset value is Nan: {} {}'.format(self.name, intensity_interval))
        else:
            raise PostOffsetEmpty('Post-offset dataframe is empty: {} {}'.format(self.name, intensity_interval))


def run(blm):
    print(blm.name, sum(map(blm.integrate_over_intensity_interval, blm.intensity_intervals)))

if __name__ == '__main__':
    st = (time.time())
    iil = IntensityIntervalsLoader()
    start = datetime(year=2016, month=4, day=4)
    end = datetime(year=2016, month=12, day=14)
    field = 'LOSS_RS12'

    iil.set_files_paths(PICKLE_INTENSITY_INTERVALS_PATH, start, end)
    iil.read_pickled_intensity_intervals()
    iil.filter_interval_by_dates(start, end)


    dcr = DosesCalculationReader()
    file_path = os.path.join(DATA_DIRs_NAMES['blm_lists'], 'blm_data_2016_nn_new.csv')
    dcr.read_csv(file_path)

    blm_names = list(dcr.get_blms(10))

    blm_loader = BLMLoader()

    blm_loader.set_files_paths('/media/sf_monitoring_analysis/data/blm_data', start, end)
    blm_loader.read_pickled_blms()
    blms = list(blm_loader.get_blms())
    import copy
    for i in blms:
        i.intensity_intervals = copy.copy(iil.intensity_intervals)
    print(time.time()-st)
    N = 4

    pool = Pool(processes=N)

    pool.map(run, blms)
    # for blm in blms:
    #     print(blm.name, sum(map(blm.integrate_over_intensity_interval, iil.intensity_intervals)))

    print(time.time()-st)


import pandas as pd
import numpy as np
import os
import sys
import pickle
import random
import time
from decimal import Decimal



def pp(out,ff):
    if ff == 1:
        print(out)


def frame_builder(dic):
    columns = ['data']
    index = list(dic.values())[0][0].tolist()
    data = list(dic.values())[0][1].tolist()
    return pd.DataFrame(data = data,index = index, columns = columns)


class intensity_interval_loader(object):
    def __init__(self,path,year = 2016):
        self.file_name = ''

        if os.path.exists(path):
            self.path = path
            self.flag_path = 0
        else:
            self.path  = ''
            self.falg_path = 1


    def file_lister(self):
        for p, d, f in os.walk(self.path):
            self.files = f
            break

    def file_loader(self):
        with open(os.path.join(self.path, self.file), 'rb') as f:
            self.intervals = pickle.load(f)

class blm_data(object):
    def __init__(self, path, name, filt):
        self.flag_full = 0
        self.flag_print = 0
        self.flag_force_save = 0

        self.directory = os.path.join(path, name)
        self.filter = filt
        self.name = name
        self.df_data = 0
        self.files = 0

    def pp(self, out):
        if self.flag_print == 1:
            print(out)

    def blm_data_file_lister(self):

        for ps, ds, fs in os.walk(self.directory):
            self.files = [f for f in fs if self.filter in f]
            break

    def blm_data_loader(self):
        d = []
        for f in self.files:
            self.pp(f)
            with open(os.path.join(self.directory, f), 'rb') as ff:
                self.dd = pickle.load(ff, encoding='latin1')
                d.append(frame_builder(self.dd))

            self.df_data = pd.concat(d)
            #             self.df_data_smothed = smoothy(self.df_data,8)

    def integrator(self, data):

        #         self.loss_interval = self.df_data[(self.df_data.index>=start)&(self.df_data.index<=end)]
        if ~data.empty:
            return np.trapz(y=data['data'], x=data.index), 0
        else:
            return 0, 1

    def offset_calc_pre(self, start, end, offset_sec=5 * 60):
        self.offset_interval_pre = self.df_data[
            (self.df_data.index >= (start - offset_sec)) & (self.df_data.index <= start)]
        self.pp(self.offset_interval_pre)
        if ~self.offset_interval_pre.empty:
            offset = np.mean(self.offset_interval_pre['data'])
            if ~np.isnan(offset):
                return offset, 0
            else:
                return 0, 2
        else:
            return 0, 1

    def offset_calc_post(self, start, end, offset_sec=5 * 60):
        self.offset_interval_post = self.df_data[
            (self.df_data.index >= (end)) & (self.df_data.index <= end + offset_sec)]
        self.pp(self.offset_interval_post)
        if ~self.offset_interval_post.empty:
            offset = np.mean(self.offset_interval_post['data'])
            if ~np.isnan(offset):
                return offset, 0
            else:
                return 0, 2
        else:
            return 0, 1

    def offset_corrector(self, integral, offset, dur):
        integral_oc = integral - (offset * dur)
        if integral_oc > 0:
            return integral_oc, 0
        if integral_oc <= 0:
            return 0, 1

    def blm_interval_analysis(self, intervals):

        for i in intervals:
            #             print(interval.start)
            if self.flag_full == 1:
                i.data_raw = self.df_data[(self.df_data.index >= i.start) & (self.df_data.index <= i.end)]
                i.integral_raw, i.integral_raw_flag = self.integrator(i.data_raw)
            else:
                i.integral_raw, i.integral_raw_flag = self.integrator(
                    self.df_data[(self.df_data.index >= i.start) & (self.df_data.index <= i.end)])

            i.offset_pre, i.offset_pre_flag = self.offset_calc_pre(i.start, i.end, 5 * 60)
            i.offset_post, i.offset_post_flag = self.offset_calc_post(i.start, i.end, 5 * 60)

            if self.flag_full == 1:
                i.offset_interval_pre = self.offset_interval_pre
                i.offset_interval_post = self.offset_interval_post

            # i.integral_oc,  i.integral_oc_flag   = self.offset_corrector(i.integral_raw,i.offset_pre,i.duration)
            if self.flag_full == 1:
                i.data_oc = i.data_raw - i.offset_pre
                i.integral_oc, i.integral_oc_flag = self.integrator(i.data_oc)
            else:
                i.integral_oc, i.integral_oc_flag = self.integrator(
                    self.df_data[(self.df_data.index >= i.start) & (self.df_data.index <= i.end)] - i.offset_pre)

        self.intervals = intervals

    def pickler(self, file_path):
        if ~os.path.exists(file_path) or self.flag_force_save == 1:
            with open(file_path, 'wb') as f:
                pickle.dump(self, f)
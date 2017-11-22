import logging
import re
import copy
from config import BLM_TYPE_REGEX_PATERN
from source.BLMInterval import BLMInterval
import _pickle as pickle
import os
from source.BLM_dose_calculation_exceptions import BLMIntervalsEmpty, BLMDataEmpty, BLMTypeNotRecognized
from sortedcontainers import SortedSet
import pandas as pd


class BLM:
    """
    The class represents a single BLM. It stores its name, a position in the LHC, a dose data and BLM intervals (periods when the beam was on).
    """

    regex_name_pattern = re.compile(r"([\w\.\-]+):(\w+)") # a regular expression pattern for extracting a BLM name and a filed name from a timber query
    date_format = '%Y_%m_%d' # a regular expression pattern for extracting a BLM name and a filed name from a timber query

    def __init__(self, name, data, position=None):
        """
        :param name: a BLM name
        :param data: a pandas dataframe which contains a BLM dose data - indices are
        :param position: a BLM position in the LHC, given in meters
        """
        self.name = name
        self.position = position
        self.data = data
        self.blm_intervals = None

    def interpolate_data(self):
        """
        The function adds new points to a BLM data. Due to differences in the data storing frequency between an intensity and  a BLM data, usually beginning of
         a subinterval (or a normal interval) is not covered by a readout in the BLM data. To make integration more accurate, those missing points are added
         using linear interpolation.
        :return:
        """
        # get all subintervals' beginnings
        subintervals_starts = sum(([sub.start for sub in blm_int.beam_modes_subintervals] for blm_int in self.blm_intervals), [])
        intervals_ends = [blm_int.end for blm_int in self.blm_intervals]
        new_indices = subintervals_starts + intervals_ends
        data = pd.concat([self.data,  pd.DataFrame(index=new_indices)])
        self.data = data[~data.index.duplicated(keep='first')].sort_index().interpolate(method='polynomial', order=1).dropna(how='any')

    def create_blm_intervals(self, intensity_intervals):
        """
        Creates BLM intervals using intensity intervals.
        :param intensity_intervals:
        :return:
        """
        self.blm_intervals = SortedSet(BLMInterval(ii.start, ii.end, ii.integrated_intensity_offset_corrected, self.get_blm_subintervals(ii)) for ii in intensity_intervals)
        return self.blm_intervals

    def get_blm_subintervals(self, intensity_interval):
        """
        It returns intensity_interval's subintervals.
        :param intensity_interval:
        :return:
        """
        try:
            return copy.deepcopy(intensity_interval.beam_modes_subintervals)
        except AttributeError as e:
            logging.warning('Intensity interval: {}\n\thas no subintervals'.format(intensity_interval))

    def get_missing_blm_intervals(self, intervals_set_container_to_check):
        """
        It compares already assigned BLM intervals with the SortedSet passed as the argument and returns "missing" intervals.
        :param SortedSet intervals_set_container_to_check:
        :return SortedSet: BLM
        """
        if self.blm_intervals is not None:
            missing_intervals = self.blm_intervals - intervals_set_container_to_check
            return missing_intervals

    def set(self, calc):
        """
        It applies a calculator passed as the argument to all BLM intervals.
        :param Calc calc: an object which inherits from the Calc class (it has to implement the run(blm_intervals) method).
        :return:
        """
        if self.blm_intervals is not None and not self.data.empty:
            calc.run(self.data, self.blm_intervals)
        else:
            if self.blm_intervals is None:
                raise BLMIntervalsEmpty('No valid {} intervals'.format(self.name))
            else:
                raise BLMDataEmpty('No data for {}'.format(self.name))

    def get_post_oc_dose(self, start=None, end=None):
        """
        It sums post offset corrected doses for BLM intervals. If the start and the end arguments are passed, it will sum only BLM intervals,
        which are fully located in [start, end] time range.
        :param datetime start: analysed time period's beginning timestamp. If None, it will analyse all available BLM intervals
        :param datetime end:  analysed time period's ending timestamp. If None it will analyse all available BLM intervals
        :return float: post offset corrected integrated dose for a required time period
        """
        return self.get_dose(lambda blm: blm.integral_post_offset_corrected, start, end)

    def get_oc_intensity_integral(self, start=None, end=None):
        """
        It sums partial intensity integrals. If the start and the end arguments are passed, it will sum only  intervals,
        which are fully located in [start, end] time range.
        :param datetime start: analysed time period's beginning timestamp. If None, it will analyse all available intervals
        :param datetime end:  analysed time period's ending timestamp. If None it will analyse all available intervals
        :return float: integrated dose for a required time period
        """
        return self.get_dose(lambda blm: blm.integrated_intensity_offset_corrected, start, end)

    def get_pre_oc_dose(self, start=None, end=None):
        """
        It sums pre offset corrected doses for BLM intervals. If the start and the end arguments are passed, it will sum only BLM intervals,
        which are fully located in [start, end] time range.
        :param datetime start: analysed time period's beginning timestamp. If None, it will analyse all available BLM intervals
        :param datetime end:  analysed time period's ending timestamp. If None it will analyse all available BLM intervals
        :return float: pre offset corrected integrated dose for a required time period
        """
        return self.get_dose(lambda blm: blm.integral_pre_offset_corrected, start, end)

    def get_pre_oc_dose_for_beam_mode(self, beam_modes, start=None, end=None):
        """
        It sums offset pre corrected doses for BLM subintervals for required beam modes. If the start and the end arguments are passed, it will consider only BLM subintervals,
        which a "parent" BLM interval in are fully located in [start, end] time range.
        :param list beam_modes: a beam modes' list, which consists integer numbers of beam modes, that will be analysed
        :param datetime start: analysed time period's beginning timestamp. If None, it will analyse all available BLM subintervals
        :param datetime end:  analysed time period's ending timestamp. If None it will analyse all available BLM subintervals
        :return float: pre offset corrected integrated dose for a required time period
        """
        if isinstance(beam_modes, int):
            beam_modes = [beam_modes]
        is_beam_mode = (lambda beam_mode: beam_mode in beam_modes)
        return self.get_dose(lambda blm: sum(sub.get_integration_result() for sub in blm.beam_modes_subintervals if is_beam_mode(sub.beam_mode)), start, end)

    def get_raw_dose(self, start=None, end=None):
        """
        It sums offset pre corrected doses for BLM subintervals for required beam modes. If the start and the end arguments are passed, it will consider only BLM subintervals,
        which a "parent" BLM interval in are fully located in [start, end] time range.
        :param list beam_modes: a beam modes' list, which consists integer numbers of beam modes, that will be analysed
        :param datetime start: analysed time period's beginning timestamp. If None, it will analyse all available BLM subintervals
        :param datetime end:  analysed time period's ending timestamp. If None it will analyse all available BLM subintervals
        :return float: pre offset corrected integrated dose for a required time period
        """
        return self.get_dose(lambda blm: blm.integral_raw, start, end)

    def get_file_name(self, start, end):
        """
        It generates a file name for the BLM.
        :param datetime start: analysed time period's beginning timestamp, which will be included in the pickle file name
        :param datetime end: analysed time period's end timestamp, which will be included in the pickle file name
        :return str: a file name, which has format: blmname_startdate_enddate_field
        """
        name_field = re.match(BLM.regex_name_pattern, self.name)
        if name_field:
            name = name_field.group(1).replace('.', '_')
            field = name_field.group(2)
            start = start.strftime(BLM.date_format)
            end = end.strftime(BLM.date_format)
            return '{0}_{1}_{2}_{3}'.format(name, start, end, field)

    def to_pickle(self, directory, start, end):
        """
        It saves a BLM to the pickle file.
        :param str directory: a path, where the BLM should be saved.
        :param datetime start: analysed time period's beginning timestamp, which will be included in the pickle file name
        :param datetime end: analysed time period's end timestamp, which will be included in the pickle file name
        :return str: a file path to the saved pickle file
        """
        self.clean_blm_intervals_from_temporary_data()
        file_path = os.path.join(directory, self.get_file_name(start, end)) + '.p'
        with open(os.path.join(directory, self.get_file_name(start, end)) + '.p', 'wb') as f:
            pickle.dump(self, f)
        return file_path

    def clean_blm_intervals_from_temporary_data(self, clean_blm_data=False):
        """
        It cleans BLM intervals from temporary data - sometimes offset or integration data are stored in order to make computations faster.
        :param bool clean_blm_data: if set to True, it will assign None to the BLM.data field.
        :return:
        """
        for blm_i in self.blm_intervals:
            blm_i.clean_data()
        if clean_blm_data:
            self.data = None

    def get_dose(self, func, start, end):
        """
        A function which shouldn't be used outside the BLM class. It implements common functionality for all kind of doses calculation - it iterates over
        BLM intervals and sums doses in those intervals.
        :param func: a function, which takes blm_interval as a parameter and returns an integrated dose
        :param datetime start: analysed time period's beginning timestamp
        :param datetime end: analysed time period's end timestamp
        :return:
        """
        if not start or not end:
            return sum(func(blm_int) for blm_int in self.blm_intervals)
        else:
            start_in_sec = start.timestamp()
            end_in_sec = end.timestamp()
            return sum(func(blm_int) for blm_int in self.blm_intervals
                       if self.is_interval_between_dates(blm_int, start_in_sec, end_in_sec))

    def is_interval_between_dates(self, blm_interval, start, end):
        """
        It checks if the blm interval given as an argument is included fully in the [start,end] time frame.
        :param BLMInterval blm_interval:
        :param datetime start: analysed time period's beginning timestamp
        :param datetime end: analysed time period's end timestamp
        :return:
        """
        return start <= blm_interval.start and blm_interval.end <= end

    def __str__(self):
        if self.blm_intervals is not None:
            return self.name + '\t\n' + '\t\n'.join(map(str, self.blm_intervals))

    def get_beam_mode_doses_as_dataframe(self, beam_modes=list(range(1,23)), start=None, end=None):
        columns = ['total dose'] + beam_modes
        total_dose = self.get_pre_oc_dose(start, end)
        values = [[self.get_pre_oc_dose_for_beam_mode(beam_mode, start, end)/total_dose for beam_mode in beam_modes]]
        values[0].insert(0, total_dose)
        return pd.DataFrame(values, columns=columns, index=[self.name])

    def get_blm_type(self):
        """
        It analyses the BLM name and returns substring, which is located after 'BLM' and before the first dot.
        :return str: BLM type
        """
        blm_type = re.match(BLM_TYPE_REGEX_PATERN, self.name)
        if blm_type:
            return blm_type.group(1)
        else:
            raise BLMTypeNotRecognized('Could not recognize {} type.'.format(self.name))


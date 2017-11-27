from datetime import datetime, timedelta,timezone
import config
from projects.LHC_intensity_calculations.source.IInterval import IInterval
import pandas as pd

beam_modes = list(range(1,23))
class BLMInterval(IInterval):
    """
    The class represents a single BLMInterval - a time period, in which beam was continuously turned on.
    """
    date_str_format = '%Y-%m-%d %X'

    def __init__(self, start, end, integrated_intensity_offset_corrected=None, beam_modes_subintervals=None):
        """

        :param float start: the staring interval's timestamp (given by seconds since the epoch)
        :param float end: the ending interval's timestamp (given by seconds since the epoch)
        :param float integrated_intensity_offset_corrected: intensity value integrated within the same time range as the BLMInterval has.
        :param SortedSet beam_modes_subintervals: the connected intensity interval's subintervals.
        """
        super().__init__(start, end)
        self.offset_pre = 0
        self.offset_pre_start = None
        self.offset_pre_end = None
        self.offset_post = 0
        self.offset_post_start = None
        self.offset_post_end = None
        self.integral_raw = 0
        self.integral_pre_offset_corrected = 0
        self.integral_post_offset_corrected = 0
        self.should_plot = None
        self.integrated_intensity_offset_corrected = integrated_intensity_offset_corrected
        self.__integration_data = None
        self.__preoffset_data = None
        self.__postoffset_data = None
        self.beam_modes_subintervals = beam_modes_subintervals

    def get_integrated_data(self, data):
        """
        It returns a data, which was used to calculated integrated dose
        :param pandas.DataFrame data: a data for the BLM
        :return: data, which was used to dose integration.
        """
        if self.__integration_data is None:
            self.__integration_data = super().get_integrated_data(data)
        return self.__integration_data

    def get_duration_for_beam_modes(self, beam_modes):
        """
        Sums durations of subintervals for given beam modes
        :return:
        """
        if isinstance(beam_modes, int):
            beam_modes = [beam_modes]
        return sum(sub.get_duration() for sub in filter(lambda subinterval: subinterval.beam_mode in beam_modes, self.beam_modes_subintervals))

    def get_as_pandas_dataframe(self):
        blm_interval = {'start': self.get_start_date_as_str(),
                        'end': self.get_end_date_as_str(),
                        'duration': self.get_duration(),
                        'intensity oc': self.integrated_intensity_offset_corrected,
                        'pre-offset': self.offset_pre,
                        'pre-offset start': self.get_date_as_str(self.offset_pre_start),
                        'pre-offset end': self.get_date_as_str(self.offset_pre_end),
                        'post-offset': self.offset_post,
                        'post-offset start': self.get_date_as_str(self.offset_post_start),
                        'post-offset end': self.get_date_as_str(self.offset_post_end),
                        'dose raw': self.integral_raw,
                        'dose pre-offset corrected': self.integral_pre_offset_corrected,
                        'dose post-offset corrected': self.integral_post_offset_corrected}

        durations = {'duration ' + str(bmode): (self.get_duration_for_beam_modes(bmode) / blm_interval['duration'] if blm_interval['duration'] != 0 else None)
                                    for bmode in beam_modes}
        subintensities = {str(bmode): (self.get_integrated_dose_for_beam_mode(bmode)/self.integral_pre_offset_corrected if self.integral_pre_offset_corrected != 0 else None)
                          for bmode in beam_modes}
        return pd.DataFrame(dict(blm_interval, **durations, **subintensities), index=[self.start])

    def get_integrated_dose_for_beam_mode(self, beam_modes):
        """
        It returns integrated dose for subinterval with specific beam modes.
        :param list beam_modes: integers list - every subinterval with the beam_mode, which appears in the list, will be taken into account during partial doses
        summing
        :return float: dose which occurred during given beam_modes
        """
        if isinstance(beam_modes, int):
            beam_modes = [beam_modes]
        return sum(sub.get_integration_result() for sub in self.beam_modes_subintervals if sub.beam_mode in beam_modes)

    def get_preoffset_data(self, data):
        """
        It returns a preoffset data, which was used to calculate pre-offset value.
        :param pandas.DataFrame data: a data for the BLM
        :return pandas.DataFrame: preoffset data, which was used to calculate pre-offset value.
        """
        if self.offset_pre_start is not None and self.offset_pre_end is not None:
            if self.__preoffset_data is None:
                self.__preoffset_data = data[(self.offset_pre_start <= data.index) & (data.index <= self.offset_pre_end)]
            return self.__preoffset_data

    def get_postoffset_data(self, data):
        """
        It returns a postoffset data, which was used to calculate post-offset value.
        :param pandas.DataFrame data: a data for the BLM
        :return pandas.DataFrame: postoffset data, which was used to calculate post-offset value.
        """
        if self.offset_pre_start is not None and self.offset_pre_end is not None:
            if self.__postoffset_data is None:
                self.__postoffset_data = data[(self.offset_post_start <= data.index) & (data.index <= self.offset_post_end)]
            return self.__postoffset_data

    def clean_data(self):
        """
        It cleans the BLM interval from temporary data, which are stored to increase performance.
        :return:
        """
        self.__integration_data = None
        self.__preoffset_data = None
        self.__postoffset_data = None

    def __str__(self):
        return 'start: {}\tend: {}\tPre-offset: {:3.1e}\tPost-offset: {:3.1e}\traw integral: {:3.1e}\tintegral_pre_oc: {:3.1e}\tintegral_post_oc: {:3.1e}'. \
            format(datetime.utcfromtimestamp(self.start).strftime(BLMInterval.date_str_format),
                   datetime.utcfromtimestamp(self.end).strftime(BLMInterval.date_str_format),
                   self.offset_pre, self.offset_post, self.integral_raw, self.integral_pre_offset_corrected, self.integral_post_offset_corrected)
from datetime import datetime, timedelta,timezone
import config
from projects.LHC_intensity_calculations.source.IInterval import IInterval


class BLMInterval(IInterval):
    """
    The class represents a single period, in which beam was continuously turned on.
    """
    date_str_format = '%Y-%m-%d %X'

    def __init__(self, start, end, integrated_intensity_offset_corrected=None, beam_modes_subintervals=None):
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
        if self.__integration_data is None:
            self.__integration_data = super().get_integrated_data(data)
        return self.__integration_data

    def get_integrated_dose_for_beam_mode(self, beam_modes):
        if isinstance(beam_modes, int):
            beam_modes = [beam_modes]
        return sum(sub.get_integration_result() for sub in self.beam_modes_subintervals if sub.beam_mode in beam_modes)

    def get_preoffset_data(self, data):
        if self.offset_pre_start is not None and self.offset_pre_end is not None:
            if self.__preoffset_data is None:
                self.__preoffset_data = data[(self.offset_pre_start <= data.index) & (data.index <= self.offset_pre_end)]
            return self.__preoffset_data

    def get_postoffset_data(self, data):
        if self.offset_pre_start is not None and self.offset_pre_end is not None:
            if self.__postoffset_data is None:
                self.__postoffset_data = data[(self.offset_post_start <= data.index) & (data.index <= self.offset_post_end)]
            return self.__postoffset_data

    def clean_data(self):
        self.__integration_data = None
        self.__preoffset_data = None
        self.__postoffset_data = None

    def __str__(self):
        return 'start: {}\tend: {}\tPre-offset: {:3.1e}\tPost-offset: {:3.1e}\traw integral: {:3.1e}\tintegral_pre_oc: {:3.1e}\tintegral_post_oc: {:3.1e}'. \
            format(datetime.utcfromtimestamp(self.start).strftime(BLMInterval.date_str_format),
                   datetime.utcfromtimestamp(self.end).strftime(BLMInterval.date_str_format),
                   self.offset_pre, self.offset_post, self.integral_raw, self.integral_pre_offset_corrected, self.integral_post_offset_corrected)
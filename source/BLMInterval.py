from datetime import datetime


class BLMInterval:
    date_str_format = '%Y-%m-%d %X'

    def __init__(self, start=None, end=None, offset_pre=0, offset_post=0, integral_raw=0,
                 integral_offset_corrected=0):
        self.start = start
        self.end = end
        self.offset_pre = offset_pre
        self.offset_post = offset_post
        self.integral_raw = integral_raw
        self.integral_offset_corrected = integral_offset_corrected

    def __str__(self):
        return 'start: {}\tend: {}\tPre-offset: {:3.1e}\tPost-offset: {:3.1e}\traw integral: {}\tintegral_oc: {}'. \
            format(datetime.utcfromtimestamp(self.start).strftime(BLMInterval.date_str_format),
                   datetime.utcfromtimestamp(self.end).strftime(BLMInterval.date_str_format),
                   self.offset_pre, self.offset_post, self.integral_raw, self.integral_offset_corrected)

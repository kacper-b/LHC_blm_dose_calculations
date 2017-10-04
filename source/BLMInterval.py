class BLMInterval:
    def __init__(self, start=None, end=None, offset_pre=None, offset_post=None, integral_raw=None, integral_offset_corrected=None):
        self.start = start
        self.end = end
        self.offset_pre = offset_pre
        self.offset_post = offset_post
        self.integral_raw = integral_raw
        self.integral_offset_corrected = integral_offset_corrected

    def __str__(self):
        return 'start: {}\tend: {}\tPre-offset: {}\tPost-offset:\t{}raw integral: {}\tintegral_oc: {}'.\
            format(self.start, self.end, self.offset_pre, self.offset_post, self.integral_raw, self.integral_offset_corrected)
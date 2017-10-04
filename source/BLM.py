from source.BLMInterval import BLMInterval
class BLM:
    def __init__(self, name, data, position=None, field=None):
        self.name = name
        self.position = position
        self.data = data
        self.field = field
        self.blm_intervals = None

    def create_blm_intervals(self, intensity_intervals):
        self.blm_intervals = [BLMInterval(start=ii.start, end=ii.end) for ii in intensity_intervals]

    def set_pre_offsets(self):
        if self.blm_intervals is not None:
            pass

    def set_post_offsets(self):
        if self.blm_intervals is not None:
            pass

    def set_raw_integrals(self):
        if self.blm_intervals is not None:
            pass

    def set_offset_corrected_integrals(self):
        if self.blm_intervals is not None:
            pass
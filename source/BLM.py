from source.BLMInterval import BLMInterval


class BLM:
    def __init__(self, name, data, position=None, field=None):
        self.name = name
        self.position = position
        self.data = data
        self.field = field
        self.blm_intervals = None

    def create_blm_intervals(self, intensity_intervals):
        blm_intervals_gen = (BLMInterval(start=ii.start, end=ii.end) for ii in intensity_intervals)
        self.blm_intervals = self.__sort_blm_intervals_by_starting_date(blm_intervals_gen)

    def __sort_blm_intervals_by_starting_date(self, blm_intervals):
        return sorted(blm_intervals, key=(lambda blm_interval: blm_interval.start))

    def set(self, calc):
        if self.blm_intervals is not None:
            calc.run(self.data, self.blm_intervals)

    def get_oc_dose(self):
        return sum((blm_int.integral_offset_corrected for blm_int in self.blm_intervals))

    def get_raw_dose(self):
        return sum(blm_int.integral_raw for blm_int in self.blm_intervals)

    def __str__(self):
        if self.blm_intervals is not None:
            return self.name + '\n' + '\n'.join(map(str, self.blm_intervals))

from source.BLM import BLM


class BLMFactory:
    def __init__(self):
        pass
    @staticmethod
    def build(intensity_intervals, blms):
        for blm_name, position in ((blm.raw_name, blm.position) for blm in blms):
            blm_scratch = BLM(name=blm_name, data=None, position=position)
            blm_scratch.create_blm_intervals(intensity_intervals)
            yield blm_scratch

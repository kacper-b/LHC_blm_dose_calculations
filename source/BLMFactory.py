from source.BLM import BLM


class BLMFactory:
    def __init__(self):
        pass

    def build(self, intensity_intervals, blm_name_position_dict):
        for blm_name, position in blm_name_position_dict.items():
            blm_scratch = BLM(name=blm_name, data=None, position=position)
            blm_scratch.create_blm_intervals(intensity_intervals)
            yield blm_scratch

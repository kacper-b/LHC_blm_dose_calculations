from Common_classes.BLM_classes.BLM import BLM


class BLMFactory:
    """
    The class allows to convert LHC_intensity_calculations's BLM class object into LHC_blm_dose_calculations's BLM class object. It assignees blm_name and position
    and creates BLM intervals using intensity intervals.
    """
    def __init__(self):
        pass

    @staticmethod
    def build(intensity_intervals, blms):
        """
        Generator which returns created BLM scratches - a BLM objects without assigned data.
        :param list intensity_intervals:
        :param list blms: a BLM object list - each object has to have raw_name field & position. Raw name is basically a BLM's name.
        :return BLM: a raw BLM objects without assigned data
        """
        for blm_name, position in ((blm.raw_name, blm.position) for blm in blms):
            blm_scratch = BLM(name=blm_name, data=None, position=position)
            blm_scratch.create_blm_intervals(intensity_intervals)
            yield blm_scratch

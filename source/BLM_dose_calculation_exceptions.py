class PreOffsetEmpty(Exception):
    pass


class PostOffsetNan(Exception):
    pass


class PreOffsetNan(Exception):
    pass


class PreOffsetStdevOverThreshold(Exception):
    pass


class PostOffsetStdevOverThreshold(Exception):
    pass


class PostOffsetEmpty(Exception):
    pass


class PreOffsetBelowZero(Exception):
    pass


class PostOffsetBelowZero(Exception):
    pass


class PreOffsetNotSetDueToNeighbourhood(Exception):
    pass


class PostOffsetNotSetDueToNeighbourhood(Exception):
    pass


class IntegrationResultBelowZero(Exception):
    pass


class IntensityIntervalNotCoveredByBLMData(Exception):
    pass


class NoBLMDataForIntensityInterval(Exception):
    pass


class BLMLoaderWrongNumberOfColumns(Exception):
    pass

class BLMDataEmpty(Exception):
    pass
class BLMIntervalsEmpty(Exception):
    pass
class PreOffsetEmpty(Exception):
    pass


class PostOffsetNan(Exception):
    pass


class PreOffsetNan(Exception):
    pass


class PostOffsetEmpty(Exception):
    pass


class PreOffsetBelowZero(Exception):
    pass


class PostOffsetBelowZero(Exception):
    pass


class IntegrationResultBelowZero(Exception):
    pass


class IntensityIntervalNotCoveredByBLMData(Exception):
    pass


class NoBLMDataForIntensityInterval(Exception):
    pass


class BLMLoaderWrongNumberOfColumns(Exception):
    pass

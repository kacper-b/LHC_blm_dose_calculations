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

class IntegrationError_IntegrationResultBelowZero(Exception):
    pass

class IntegrationError_IIntervalNotCoveredByBLMData(Exception):
    pass

class IntegrationError_NoBLMDataForIInterval(Exception):
    pass

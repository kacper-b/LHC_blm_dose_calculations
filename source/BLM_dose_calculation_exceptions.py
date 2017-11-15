import logging

class ExceptionLogging:
    def __init__(self, logging_func):
        self.logging_func = logging_func

class PreOffsetEmpty(Exception, ExceptionLogging):
    def __init__(self, msg):
        self.logging_func = logging.debug
        super(self.__class__, self).__init__(msg)
    pass


class PostOffsetNan(Exception, ExceptionLogging):
    def __init__(self, msg):
        self.logging_func = logging.debug
        super(self.__class__, self).__init__(msg)
    pass


class PreOffsetNan(Exception, ExceptionLogging):
    def __init__(self, msg):
        self.logging_func = logging.debug
        super(self.__class__, self).__init__(msg)
    pass


class PreOffsetStdevOverThreshold(Exception, ExceptionLogging):
    def __init__(self, msg):
        self.logging_func = logging.debug
        super(self.__class__, self).__init__(msg)
    pass


class PostOffsetStdevOverThreshold(Exception, ExceptionLogging):
    def __init__(self, msg):
        self.logging_func = logging.debug
        super(self.__class__, self).__init__(msg)
    pass


class PostOffsetEmpty(Exception, ExceptionLogging):
    def __init__(self, msg):
        self.logging_func = logging.debug
        super(self.__class__, self).__init__(msg)
    pass


class PreOffsetBelowZero(Exception, ExceptionLogging):
    def __init__(self, msg):
        self.logging_func = logging.debug
        super(self.__class__, self).__init__(msg)
    pass


class PostOffsetBelowZero(Exception, ExceptionLogging):
    def __init__(self, msg):
        self.logging_func = logging.debug
        super(self.__class__, self).__init__(msg)
    pass


class PreOffsetNotSetDueToNeighbourhood(Exception, ExceptionLogging):
    def __init__(self, msg):
        self.logging_func = logging.debug
        super(self.__class__, self).__init__(msg)
    pass


class PostOffsetNotSetDueToNeighbourhood(Exception, ExceptionLogging):
    def __init__(self, msg):
        self.logging_func = logging.debug
        super(self.__class__, self).__init__(msg)
    pass


class IntegrationResultBelowZero(Exception, ExceptionLogging):
    def __init__(self, msg):
        self.logging_func = logging.debug
        super(self.__class__, self).__init__(msg)
    pass

class IntegrationResultIsNan(Exception, ExceptionLogging):
    def __init__(self, msg):
        self.logging_func = logging.warning
        super(self.__class__, self).__init__(msg)
    pass

class IntensityIntervalNotCoveredByBLMData(Exception, ExceptionLogging):
    def __init__(self, msg):
        self.logging_func = logging.warning
        super(self.__class__, self).__init__(msg)
    pass

class IntensitySubIntervalNotCoveredByBLMData(Exception, ExceptionLogging):
    def __init__(self, msg):
        self.logging_func = logging.warning
        super(self.__class__, self).__init__(msg)
    pass


class NoBLMDataForIntensityInterval(Exception, ExceptionLogging):
    def __init__(self, msg):
        self.logging_func = logging.error
        super(self.__class__, self).__init__(msg)
    pass


class NoBLMDataForIntensitySubInterval(Exception, ExceptionLogging):
    def __init__(self, msg):
        self.logging_func = logging.error
        super(self.__class__, self).__init__(msg)
    pass

class BLMLoaderWrongNumberOfColumns(Exception, ExceptionLogging):
    def __init__(self, msg):
        self.logging_func = logging.error
        super(self.__class__, self).__init__(msg)
    pass


class BLMDataEmpty(Exception, ExceptionLogging):
    def __init__(self, msg):
        self.logging_func = logging.critical
        super(self.__class__, self).__init__(msg)
    pass


class BLMIntervalsEmpty(Exception, ExceptionLogging):
    def __init__(self, msg):
        self.logging_func = logging.critical
        super(self.__class__, self).__init__(msg)
    pass

class BLMInvalidRawData(Exception, ExceptionLogging):
    def __init__(self, msg):
        self.logging_func = logging.error
        super(self.__class__, self).__init__(msg)
    pass


class BLMTypeNotRecognized(Exception, ExceptionLogging):
    def __init__(self, msg):
        self.logging_func = logging.critical
        super(self.__class__, self).__init__(msg)
    pass

class NormalizedIntensityPlotRangeTooSmall(Exception, ExceptionLogging):
    def __init__(self, msg):
        self.logging_func = logging.critical
        super(self.__class__, self).__init__(msg)
    pass
class NormalizedLuminosityPlotRangeTooSmall(Exception, ExceptionLogging):
    def __init__(self, msg):
        self.logging_func = logging.critical
        super(self.__class__, self).__init__(msg)
    pass
class WrongBLMFunctionName(Exception, ExceptionLogging):
    def __init__(self, msg):
        self.logging_func = logging.critical
        super(self.__class__, self).__init__(msg)
    pass

import logging
from Common_classes.Interfaces.ExceptionLogging import ExceptionLogging


class PreOffsetEmpty(Exception, ExceptionLogging):
    """
    This exception occurs when a data that should be used to pre offset calculation is empty.
    """
    def __init__(self, msg):
        self.logging_func = logging.debug
        super(self.__class__, self).__init__(msg)
    pass


class PostOffsetNan(Exception, ExceptionLogging):
    """
    This exception occurs when a calculated post offset isn't valid number.
    """
    def __init__(self, msg):
        self.logging_func = logging.debug
        super(self.__class__, self).__init__(msg)
    pass


class PreOffsetNan(Exception, ExceptionLogging):
    """
    This exception occurs when a calculated pre offset isn't valid number.
    """
    def __init__(self, msg):
        self.logging_func = logging.debug
        super(self.__class__, self).__init__(msg)
    pass


class PreOffsetStdevOverThreshold(Exception, ExceptionLogging):
    """
    This exception occurs when a data that should be used to pre offset calculation has stddev above threshold.
    """
    def __init__(self, msg):
        self.logging_func = logging.debug
        super(self.__class__, self).__init__(msg)
    pass


class PostOffsetStdevOverThreshold(Exception, ExceptionLogging):
    """
    This exception occurs when a data that should be used to post offset calculation has stddev above threshold.
    """
    def __init__(self, msg):
        self.logging_func = logging.debug
        super(self.__class__, self).__init__(msg)
    pass


class PostOffsetEmpty(Exception, ExceptionLogging):
    """
    This exception occurs when a data that should be used to post offset calculation is empty.
    """
    def __init__(self, msg):
        self.logging_func = logging.debug
        super(self.__class__, self).__init__(msg)
    pass


class PreOffsetNotSetDueToNeighbourhood(Exception, ExceptionLogging):
    """
    This exception occurs when a data that should be used to the pre offset calculation overlaps period when the beam was on.
    """
    def __init__(self, msg):
        self.logging_func = logging.debug
        super(self.__class__, self).__init__(msg)
    pass


class PostOffsetNotSetDueToNeighbourhood(Exception, ExceptionLogging):
    """
    This exception occurs when a data that should be used to the post offset calculation overlaps period when the beam was on.
    """
    def __init__(self, msg):
        self.logging_func = logging.debug
        super(self.__class__, self).__init__(msg)
    pass


class IntegrationResultBelowZero(Exception, ExceptionLogging):
    """
    This exception occurs when an integrated value (ex. dose) is below 0.
    """
    def __init__(self, msg):
        self.logging_func = logging.debug
        super(self.__class__, self).__init__(msg)
    pass


class IntegrationResultIsNan(Exception, ExceptionLogging):
    """
    This exception occurs when an integrated value (ex. dose) is Nan.
    """
    def __init__(self, msg):
        self.logging_func = logging.warning
        super(self.__class__, self).__init__(msg)
    pass


class NoBLMDataForIntensityInterval(Exception, ExceptionLogging):
    """
    This exception occurs when an intensity interval is not covered by a BLM data.
    """
    def __init__(self, msg):
        self.logging_func = logging.error
        super(self.__class__, self).__init__(msg)
    pass


class NoBLMDataForIntensitySubInterval(Exception, ExceptionLogging):
    """
    This exception occurs when an intensity subinterval is not covered by a BLM data.
    """
    def __init__(self, msg):
        self.logging_func = logging.error
        super(self.__class__, self).__init__(msg)
    pass

class NormalizedIntensityPlotRangeTooSmall(Exception, ExceptionLogging):
    """
    This exception occurs when an intensity normalized plot range does not cover all plot points.
    """
    def __init__(self, msg):
        self.logging_func = logging.critical
        super(self.__class__, self).__init__(msg)
    pass


class NormalizedLuminosityPlotRangeTooSmall(Exception, ExceptionLogging):
    """
    This exception occurs when an luminosity normalized plot range does not cover all plot points.
    """
    def __init__(self, msg):
        self.logging_func = logging.critical
        super(self.__class__, self).__init__(msg)
    pass


class WrongBLMFunctionName(Exception, ExceptionLogging):
    """
    This exception occurs when user provides an unexpected function name.
    """
    def __init__(self, msg):
        self.logging_func = logging.critical
        super(self.__class__, self).__init__(msg)
    pass

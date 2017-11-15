from abc import ABC, abstractmethod


class Calc(ABC):
    """
    Abstract class for every calculator. Each one must implement run method, which takes data and a blm_interval list
    and performs calculations using that variables.
    """
    @abstractmethod
    def run(self, data, blm_intervals):
        """
        Abstract method which should perform some calculations on blm_interval list.
        :param data:
        :param blm_intervals:
        :return:
        """
        pass

    def __str__(self):
        return str(self.__class__.__name__)

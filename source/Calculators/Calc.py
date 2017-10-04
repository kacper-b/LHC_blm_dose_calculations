from abc import ABC, abstractmethod


class Calc(ABC):
    @abstractmethod
    def run(self, data, blm_intervals):
        pass

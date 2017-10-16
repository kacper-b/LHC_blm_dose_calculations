from source.Calculators.Calc import Calc
from datetime import datetime
import os
import numpy as np
import matplotlib.dates as md
import matplotlib.pyplot as plt
import pandas as pd
import re
from abc import ABC, abstractmethod


class IPlotter(ABC):
    def save_plot(self, file_path):
        plt.legend(loc='best')
        plt.savefig(file_path, bbox_inches='tight')

    def clear(self):
        plt.clf()
        plt.cla()
        plt.close()

    def show(self):
        plt.show()

    def legend(self):
        plt.tight_layout()
        plt.legend()
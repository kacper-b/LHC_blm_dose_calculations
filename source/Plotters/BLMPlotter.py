from source.Calculators.Calc import Calc
from datetime import datetime
import os
import matplotlib.dates as md
import matplotlib.pyplot as plt
import pandas as pd
import re
import numpy as np
from source.Plotters.IPlotter import IPlotter


class BLMsPlotter(IPlotter):
    plt.style.use('ggplot')
    regex_name_pattern = re.compile(r"([\w\.]+):(\w+)")
    date_format = '%Y_%m_%d_%H%M'

    def __init__(self, output_directory):
        self.output_directory = output_directory


if __name__ == '__main__':
    p = BLMsPlotter(None)
    p.plot(None)
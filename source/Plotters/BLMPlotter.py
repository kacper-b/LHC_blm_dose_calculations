import matplotlib.pyplot as plt
import re
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
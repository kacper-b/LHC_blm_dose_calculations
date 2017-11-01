import numpy as np
import matplotlib.pyplot as plt
from abc import ABC


class IPlotter(ABC):
    def save_plot(self, file_path):
        plt.legend(loc='best')
        plt.savefig(file_path, bbox_inches='tight')

    def save_plot_data(self, file_path, x, y):
        np.savetxt(file_path, np.column_stack((x,y)), delimiter='\t', header='x\ty')

    def save_plot_and_data(self, file_path_name_without_extension, blm_positions, integrated_doses):
        self.save_plot(file_path_name_without_extension + '.png')
        self.save_plot(file_path_name_without_extension + '.pdf')
        self.save_plot_data(file_path_name_without_extension + '.txt', blm_positions, integrated_doses)

    def clear(self):
        plt.clf()
        plt.cla()
        plt.close()

    def show(self):
        plt.show()

    def legend(self):
        plt.tight_layout()
        plt.legend()
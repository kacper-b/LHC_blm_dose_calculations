import matplotlib.pyplot as plt
from abc import ABC
import pandas as pd

class IPlotter(ABC):
    def save_plot(self, file_path):
        plt.legend(loc='best')
        plt.savefig(file_path, bbox_inches='tight')

    def save_plot_data(self, file_path, x, y, blm_names):
        results = pd.DataFrame(list(zip(x,y)), columns=['dcum', 'y'], index=map(lambda blm_name: blm_name.decode('UTF-8'),blm_names))
        results.to_csv(file_path, sep='\t')

    def save_plot_and_data(self, file_path_name_without_extension, blm_positions, integrated_doses, blm_names):
        self.save_plot(file_path_name_without_extension + '.png')
        self.save_plot(file_path_name_without_extension + '.pdf')
        self.save_plot_data(file_path_name_without_extension + '.txt', blm_positions, integrated_doses, blm_names)

    def clear(self):
        plt.clf()
        plt.cla()
        plt.close()

    def show(self):
        plt.show()

    def legend(self):
        plt.tight_layout()
        plt.legend()
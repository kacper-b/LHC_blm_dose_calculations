import matplotlib.pyplot as plt
from abc import ABC
import pandas as pd
import config
class IPlotter(ABC):
    lhc_elements = sorted([[(ip[0], ip[0])] + ip[1:] for ip in config.IPs] + [
        [(config.ARC_DISTANCE_OFFSET + (config.IPs[ip[1] - 1][0] if ip[1] != 8 else ip[0]),
          -config.ARC_DISTANCE_OFFSET + (config.IPs[ip[1]][0] if ip[1] != 8 else config.LHC_LENGTH)),
         8 + ip[1],
         'arc_{}{}'.format(ip[1], config.IPs[ip[1] if ip[1] != 8 else 0][1]), None] for ip in config.IPs], key=lambda x: x[0][0])

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

    def get_fully_covered_lhc_section(self, dcum_start, dcum_end):
        if dcum_start < 0:
            dcum_start+=config.LHC_LENGTH
        start, end = '', ''

        for index, section in enumerate(self.lhc_elements):
            element_position_end = section[0][1]
            if element_position_end > dcum_end:
                end = self.lhc_elements[index - 1][2]
                break
        if dcum_end >= dcum_start:
            for index, section in enumerate(self.lhc_elements):
                element_position_start = section[0][0]
                if element_position_start >= dcum_start:
                    start = self.lhc_elements[index][2]
                    break
        else:
            lhc_elements_reversed = list(reversed(self.lhc_elements))
            for index, section in enumerate(lhc_elements_reversed):
                element_position_start = section[0][0]
                if dcum_start > element_position_start:
                    start = lhc_elements_reversed[index-1][2]
                    break
        if start == end:
            out = '_' + start
        elif start:
            out = '_' + start + '-' + end
        else:
            out = ''

        out+= '_dcum_{}_{}'.format(int(dcum_start), int(dcum_end))
        return out
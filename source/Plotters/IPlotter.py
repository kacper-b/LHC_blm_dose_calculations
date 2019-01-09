import matplotlib.pyplot as plt
from abc import ABC
import pandas as pd
from configurations.config import ARC_DISTANCE_OFFSET, IPs,LHC_LENGTH


def get_LHC_sectors():
    """
    It's impossible to decrypt the following few lines, so don't even try. The function creates dataframe which
    is used during conversion from a DCUM to a LHC sector name
    :return: dataframe which contains dcum ranges and names of sectors in the LHC.
    """
    lhc_elements = sorted([[(ip[0] - ARC_DISTANCE_OFFSET, ip[0] + ARC_DISTANCE_OFFSET)] + ip[1:2] + [ip[2].replace('P', 'R')] + ip[3:] for ip in IPs] +
                          [[(ARC_DISTANCE_OFFSET + (IPs[ip[1] - 1][0] if ip[1] != 8 else ip[0]),
                             -ARC_DISTANCE_OFFSET + (IPs[ip[1]][0] if ip[1] != 8 else LHC_LENGTH)),
                            8 + ip[1],
                            'arc{}{}'.format(ip[1], IPs[ip[1] if ip[1] != 8 else 0][1]), None] for ip in IPs], key=lambda x: x[0][0])

    lhc_el = list([i[0][0], i[0][1]] + i[1:] for i in lhc_elements)

    df_lhc_el = pd.DataFrame(lhc_el, columns=['start', 'end', 'not_important', 'info', 'not_important'])
    df_lhc_el_n = df_lhc_el.copy()
    df_lhc_el_n['start'] = df_lhc_el_n['start'] - [LHC_LENGTH]
    df_lhc_el_n['end'] = df_lhc_el_n['end'] - [LHC_LENGTH]
    df_lhc_el_c = pd.concat([df_lhc_el_n, df_lhc_el])
    return df_lhc_el_c


class IPlotter(ABC):
    """
    Abstract class for plotting classes. It implements common functions like name creation or saving.
    """
    lhc_elements = get_LHC_sectors()

    def save_plot(self, file_path):
        """
        Saves plot as an image.
        :param str file_path:
        :return:
        """
        # plt.legend(loc='best')
        plt.savefig(file_path, bbox_inches='tight', dpi=200)

    def save_plot_data(self, file_path, x, y, blm_names):
        """
        Saves BLM doses showed on a plot.
        :param str file_path:
        :param list x: arguments
        :param list y: values
        :param list blm_names:
        :return:
        """
        results = pd.DataFrame(list(zip(x, y)), columns=['dcum', 'y'], index=blm_names)
        results.to_csv(file_path, sep='\t')

    def save_plot_and_data(self, file_path_name_without_extension, blm_positions, integrated_doses, blm_names):
        """
        Saves plot and plot data.
        :param file_path_name_without_extension:
        :param blm_positions:
        :param integrated_doses:
        :param blm_names:
        :return:
        """
        self.save_plot(file_path_name_without_extension + '.png')
        self.save_plot(file_path_name_without_extension + '.pdf')
        self.save_plot_data(file_path_name_without_extension + '.txt', blm_positions, integrated_doses, blm_names)

    def clear(self):
        """
        Clears settings and plots.
        :return:
        """
        plt.clf()
        plt.cla()
        plt.close()

    def show(self):
        """
        Shows a plot on a screen.
        :return:
        """
        plt.show()

    def legend(self):
        """
        Adds a legend to a plot.
        :return:
        """
        plt.tight_layout()
        plt.legend()

    def get_fully_covered_lhc_section(self, dcum_start, dcum_end):
        """
        Converts dcum_start and dcum
        :param dcum_start: the first BLM's DCUM in meters
        :param dcum_end: the last BLM's DCUM in meters
        :return: sectors
        """
        df_part = self.lhc_elements[(self.lhc_elements['end'] >= dcum_start) & (self.lhc_elements['start'] <= dcum_end)]
        if len(df_part['info']) <= 2:
            out = '_'.join(df_part['info']) + '_{:+06d}_{:+06d}'.format(int(dcum_start), int(dcum_end))
        else:
            out = '{}_{}_{:+06d}_{:+06d}'.format(df_part['info'].iloc[0], df_part['info'].iloc[-1], int(dcum_start), int(dcum_end))
        return out
    

if __name__ == '__main__':
    print(IPlotter.lhc_elements)
import matplotlib.pyplot as plt
from abc import ABC
import pandas as pd
import config
from config import ARC_DISTANCE_OFFSET, IPs,LHC_LENGTH

class IPlotter(ABC):
    lhc_elements = sorted([[(ip[0] - ARC_DISTANCE_OFFSET, ip[0] + ARC_DISTANCE_OFFSET)] + ip[1:2]+[ip[2].replace('P','R')]+ip[3:] for ip in IPs] + [
        [(ARC_DISTANCE_OFFSET + (IPs[ip[1] - 1][0] if ip[1] != 8 else ip[0]),
          -ARC_DISTANCE_OFFSET + (IPs[ip[1]][0] if ip[1] != 8 else LHC_LENGTH)),
         8 + ip[1],
         'arc{}{}'.format(ip[1], IPs[ip[1] if ip[1] != 8 else 0][1]), None] for ip in IPs], key=lambda x: x[0][0])

    lhc_el = list([i[0][0], i[0][1]] + i[1:] for i in lhc_elements)
    df_lhc_el = pd.DataFrame(lhc_el, columns=['start', 'end', 'wtf1', 'info', 'wtf2'])

    df_lhc_el_n = df_lhc_el.copy()
    df_lhc_el_n['start'] = df_lhc_el_n['start'] - [LHC_LENGTH]
    df_lhc_el_n['end'] = df_lhc_el_n['end'] - [LHC_LENGTH]

    df_lhc_el_c = pd.concat([df_lhc_el_n, df_lhc_el])
    # df_lhc_el_c

    def save_plot(self, file_path):
        plt.legend(loc='best')
        plt.savefig(file_path, bbox_inches='tight', dpi=300)

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
        df_part = self.df_lhc_el_c[(self.df_lhc_el_c['end'] >= dcum_start) & (self.df_lhc_el_c['start'] <= dcum_end)]
        if len(df_part['info']) <= 2:
            out = '_'.join(df_part['info']) + '_{:+06d}_{:+06d}'.format(int(dcum_start), int(dcum_end))
        else:
            out = '{}_{}_{:+06d}_{:+06d}'.format(df_part['info'].iloc[0], df_part['info'].iloc[-1], int(dcum_start),
                                                 int(dcum_end))
        return out
    
    #
    # lhc_elements = sorted([[(ip[0], ip[0])] + ip[1:] for ip in IPs] + [
    #     [(ARC_DISTANCE_OFFSET + (IPs[ip[1] - 1][0] if ip[1] != 8 else ip[0]),
    #       -ARC_DISTANCE_OFFSET + (IPs[ip[1]][0] if ip[1] != 8 else LHC_LENGTH)),
    #      8 + ip[1],
    #      'arc_{}{}'.format(ip[1], IPs[ip[1] if ip[1] != 8 else 0][1]), None] for ip in IPs], key=lambda x: x[0][0])
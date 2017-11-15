from config import LHC_LENGTH, IPs
import pandas as pd

from source.BLM_dose_calculation_exceptions import WrongBLMFunctionName


class BLMFilter:
    def __init__(self):
        self.df_ips = self.get_ips()
        self.filter_functions = {'arc': lambda IP_num, left_offset, right_offset: lambda blm: self.is_blm_in_arc_after_ip(blm, IP_num, left_offset, right_offset),
                                 'ir': lambda IP_num, left_offset, right_offset: lambda blm: self.is_blm_in_ip_neighbourhood(blm, IP_num, left_offset, right_offset),
                                 'all': lambda IP_num, left_offset, right_offset: lambda blm: True}

    def filter_blms(self, blms, func=lambda blm: True):
        return filter(func, blms)

    def get_ips(self):
        df_ips = pd.DataFrame(IPs, columns=['dcum', 'ipn', 'ip', 'pos'])
        df_ips.index = df_ips['dcum']
        return df_ips

    def get_IP_position(self, IP_num):
        return self.df_ips[self.df_ips['ipn'] == IP_num]['dcum'].values[0]

    def is_blm_in_ip_neighbourhood(self, blm, ip_num, left_offset=700, right_offset=700):
        ip_position = self.get_IP_position(ip_num)
        sector_start = ip_position - left_offset
        sector_end = ip_position + right_offset
        lhc_len = LHC_LENGTH

        if blm.position < 0:
            blm.position += lhc_len
        if 0 <= sector_start < blm.position < sector_end <= lhc_len:
            return True
        elif sector_start < 0 and sector_end <= lhc_len <= blm.position - sector_start:
            blm.position -= lhc_len
            return True
        elif sector_start < 0 <= blm.position <= sector_end <= lhc_len:
            return True
        return False

    def is_blm_in_arc_after_ip(self, blm, ip_num, left_offset=700, right_offset=700):
        ip_next = ip_num + 1 if ip_num != 8 else 1
        ip1_position = self.get_IP_position(ip_num)
        ip2_position = self.get_IP_position(ip_next)
        return self.is_blm_in_ip_neighbourhood(blm, ip_num, -left_offset, (ip2_position if ip_next != 1 else LHC_LENGTH) - ip1_position - right_offset)

    def get_filter_function(self, what_to_plot, ip_num=1, left_offset=700, right_offset=700):
        try:
            return self.filter_functions[what_to_plot](ip_num, left_offset, right_offset)
        except KeyError as e:
            raise WrongBLMFunctionName('{} is not valid function name. Possible names: {}'.format(what_to_plot, ', '.join(self.filter_functions.keys())))


if __name__ == '__main__':
    blm_filter = BLMFilter()
    blm_filter.get_filter_function('aa')

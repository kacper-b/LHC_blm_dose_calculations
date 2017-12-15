from config import LHC_LENGTH, IPs
import pandas as pd

from source.BLM_dose_calculation_exceptions import WrongBLMFunctionName


class BLMFilter:
    """
    The class provides tools to filter BLMs by DCUM and selects ones that are located in the specific area (ex. arc or intersection region).
    """
    def __init__(self):
        self.df_ips = self.get_ips()
        self.filter_functions = {'arc': lambda IP_num, left_offset, right_offset: lambda blm: self.is_blm_in_arc_after_ip(blm, IP_num, left_offset, right_offset),
                                 'ir': lambda IP_num, left_offset, right_offset: lambda blm: self.is_blm_in_ip_neighbourhood(blm, IP_num, left_offset, right_offset),
                                 'all': lambda IP_num, left_offset, right_offset: lambda blm: True}

    def filter_blms(self, blms, func=lambda blm: True):
        """
        It filters blms using a given function.
        :param list blms:
        :param lambda func: a function which takes blm as an argument and returns logical value
        :return filter: a filter object which contains only those BLM, for which the passed function returned True
        """
        return filter(func, blms)

    def get_ips(self):
        """
        It creates the DataFrame with the LHC intersection points' parameters ('dcum', 'ipn', 'ip', 'pos').
        :return pandas.DataFrame:
        """
        df_ips = pd.DataFrame(IPs, columns=['dcum', 'ipn', 'ip', 'pos'])
        df_ips.index = df_ips['dcum']
        return df_ips

    def get_IP_position(self, IP_num):
        """
        It returns an intersection point position.
        :param int IP_num: number from range [1:8]
        :return float: dcum in meters
        """
        return self.df_ips[self.df_ips['ipn'] == IP_num]['dcum'].values[0]

    def is_blm_in_ip_neighbourhood(self, blm, ip_num, left_offset=700, right_offset=700):
        """
        The function checks if a given BLM is located in the IP area.
        :param BLM blm: a BLM class object which contains the BLM position
        :param int ip_num: IP number. One of {1,2,3,4,5,6,7,8}
        :param float left_offset: it tells how many meters before the IP position should be considered
        :param float right_offset: it tells how many meters after the IP position should be considered
        :return bool: True if the BLM is located in the IP area
        """
        ip_position = self.get_IP_position(ip_num)
        sector_start = ip_position - left_offset
        sector_end = ip_position + right_offset
        lhc_len = LHC_LENGTH

        # If somehow the BLM position is < 0, it means that real dcum of that BLM is lhc_len - abs(blm.position)
        if blm.position < 0:
            blm.position += lhc_len

        # If both start and end sectors are in positive dcums domain
        if 0 <= sector_start < blm.position < sector_end <= lhc_len:
            return True

        # If the sector start is < 0, sector end > 0 and blm is located on the left side of IP 1
        elif sector_start < 0 and sector_end <= lhc_len <= blm.position - sector_start:
            blm.position -= lhc_len
            return True

        # If the sector start is < 0, sector end > 0 and blm is located on the right side of IP 1
        elif sector_start < 0 <= blm.position <= sector_end <= lhc_len:
            return True
        return False

    def is_blm_in_arc_after_ip(self, blm, ip_num, left_offset=700, right_offset=700):
        """
        The function checks if a given BLM is located in the arc after an IP.
        :param BLM blm: a BLM class object which contains the BLM position
        :param int ip_num: IP number. One of {1,2,3,4,5,6,7,8}
        :param float left_offset:
        if what_to_plot is equal to 'arc' then the arc starts left_offset after the IP position.
        if what_to_plot is equal to 'ir' then the interesting area starts left_offset meters before the IP position
        :param float right_offset:
        if what_to_plot is equal to 'arc' then the arc ends right_offset meters before the next IP position.
        if what_to_plot is equal to 'ir' then the interesting area ends right_offset meters after the IP position
        :return bool: True if the BLM is located in the arc after IP
        """
        ip_next = ip_num + 1 if ip_num != 8 else 1
        ip1_position = self.get_IP_position(ip_num)
        ip2_position = self.get_IP_position(ip_next)
        return self.is_blm_in_ip_neighbourhood(blm, ip_num, -left_offset, (ip2_position if ip_next != 1 else LHC_LENGTH) - ip1_position - right_offset)

    def get_filter_function(self, what_to_plot, ip_num=1, left_offset=700, right_offset=700):
        """
        It returns a function (one of BLMFilter.filter_functions) which takes a BLM class object as an argument and returns logical value which tells
        if the BLM should be analyzed. By setting what_to_plot it is possible to select only a specific IR section or an arc.

        :param str what_to_plot: one of BLMFilter.filter_functions keys.
        'arc' means that the arc after the given IP should be considered ;
        'ir' means that the area of the given IP should be considered;
        'all' means that all BLMs should be considered.
        :param int ip_num: IP number. One of {1,2,3,4,5,6,7,8}

        :param float left_offset:
        if what_to_plot is equal to 'arc' then the arc starts left_offset after the IP position.
        if what_to_plot is equal to 'ir' then the interesting area starts left_offset meters before the IP position

        :param float right_offset:
        if what_to_plot is equal to 'arc' then the arc ends right_offset meters before the next IP position.
        if what_to_plot is equal to 'ir' then the interesting area ends right_offset meters after the IP position
        :return:
        """
        try:
            return self.filter_functions[what_to_plot](ip_num, left_offset, right_offset)
        except KeyError as e:
            raise WrongBLMFunctionName('{} is not valid function name. Possible names: {}'.format(what_to_plot, ', '.join(self.filter_functions.keys())))


if __name__ == '__main__':
    blm_filter = BLMFilter()
    blm_filter.get_filter_function('aa')

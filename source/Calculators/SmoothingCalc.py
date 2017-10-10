from source.Calculators.Calc import Calc
from statsmodels.nonparametric.smoothers_lowess import lowess
import pandas as pd


class SmoothingCalc(Calc):
    def __init__(self, points=6):
        self.points = points

    def run(self, data, blm_intervals=None):
        self.__smoothy(data)

    def __smoothy(self, data):
        column_name = data.columns[0]
        y = data[column_name]
        x = data.index
        data_len = len(x)
        dn = lowess(y, x, frac=self.points / data_len)
        data2 = pd.DataFrame(data=dn[:, 1], index=dn[:, 0], columns=[column_name])
        data.update(data2)

if __name__ == '__main__':
    # TESTs
    import numpy as np
    c = SmoothingCalc()
    t = np.linspace(0,10,100)
    x = np.sin(t)
    noise = np.random.uniform(-0.5,.5,100)
    xx = x+noise
    data = pd.DataFrame(data={'noise':xx}, index=t)
    data2 = pd.DataFrame(data={'noise':xx}, index=t)

    c.run(data)
    import matplotlib
    matplotlib.use
    import matplotlib.pyplot as plt
    plt.style.use('ggplot')
    data.plot()
    data2.plot()
    plt.show()
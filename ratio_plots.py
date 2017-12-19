from config import PLOTS_DIR_PATH, RESULTS_DIR_PATH
from Plotting.python.plotting_layout import *
import matplotlib.pyplot as plt
# import matplotlib
# from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
# matplotlib.style.use('ggplot')
# %matplotlib inline

# Add submodules to path
with open('.gitmodules') as f:
    content = f.read()
    for submodule_dir_name in re.findall(r"^\s*path\s*\=\s(\w+)$", content, re.MULTILINE):
        sys.path.insert(0, submodule_dir_name)

_TID_DATA_DIR = os.path.join(RESULTS_DIR_PATH,'result_LHC_blm_dose_calculations')
PLOT_DIR = PLOTS_DIR_PATH

def year_compare(year_info_1, year_info_2, normalizer):
    file_1 = year_info_1['file']
    info_1 = year_info_1['info']
    file_2 = year_info_2['file']
    info_2 = year_info_2['info']

    with open(os.path.join(_TID_DATA_DIR, file_1), 'r') as f:
        data_1 = pd.read_table(f, sep='\t', header=0, names=['TID_1'], index_col=0)

    with open(os.path.join(_TID_DATA_DIR, file_2), 'r') as f:
        data_2 = pd.read_table(f, sep='\t', header=0, names=['TID_2'], index_col=0)

    _data = pd.concat([data_1, data_2], axis=1).dropna(axis=0, how='any')

    _data['1/2'] = _data['TID_1'] / _data['TID_2']

    print(np.mean(_data['1/2']))
    print(np.std(_data['1/2']))

    pl = plotter_layout()
    pl.start = _data.index[0]
    pl.end = _data.index[-1]
    fig = plt.figure(figsize=(16, 8))
    fig.subplots_adjust(hspace=.001)

    ax1 = plt.subplot2grid((3, 2), (0, 0), colspan=3, rowspan=2)
    ax1.set_title('Ratio of the {} and {} data \n data normalized with {}'.format(info_1, info_2, normalizer),
                  fontsize=16)
    ax1.set_xlim(pl.start, pl.end)
    ax1.set_ylim(0, 3)
    ax1.set_ylabel('Ratio')
    ax1.text(pl.start + 0.05 * (pl.end - pl.start), 2.5, r'$\mu$ : {:.2f}'.format(np.mean(_data['1/2'])), fontsize=15)
    ax1.text(pl.start + 0.05 * (pl.end - pl.start), 2.25, r'$\sigma$ :{:.2f}'.format(np.std(_data['1/2'])), fontsize=15)
    #     ax1.set_yaxis(fontsize = 14)
    ax1.text(pl.start + 0.5 * (pl.end - pl.start), 1.5, 'Preliminary', va='center', ha='center', alpha=.2, fontsize=46,
             rotation=45)
    ax1.tick_params(axis='y', labelsize=12)
    ax1.plot((pl.start, pl.end), (1, 1), 'k')
    ax1.plot(_data.index, _data['1/2'], label=info_1 + '/' + info_2)
    ax1.legend(loc=1, fontsize=14)
    ax2 = plt.subplot2grid((3, 2), (2, 0), colspan=3)
    pl.x_off = 0
    pl.plotter_layout(ax2, 0, 1)
    ax2.text(pl.start + 0.95 * (pl.end - pl.start), -7.5, 'courtesy MCWG', va='center', ha='right', alpha=.2,
             fontsize=14)
    return fig



_1_data_file = 'n_lum_TID2017-05-01_2017-10-15_dcum_-406_406.txt'
_2_data_file = 'n_lum_TID2016-04-03_2016-10-30_dcum_-406_406.txt'

normalizer = 'luminosity'
info_2017 = {'file':_1_data_file,'info':'2017_blm'}
info_2016 = {'file':_2_data_file,'info':'2016_blm'}

fig = year_compare(info_2017,info_2016,normalizer)
fig.savefig(os.path.join(PLOT_DIR,'LHC_ratio','ratio_2017_2016_IP1.pdf'))
fig.savefig(os.path.join(PLOT_DIR,'LHC_ratio','ratio_2017_2016_IP1.png'))


_1_data_file = 'n_lum_TID2017-05-01_2017-10-15_dcum_12932_13726.txt'
_2_data_file = 'n_lum_TID2016-04-03_2016-10-30_dcum_12932_13726.txt'

normalizer = 'luminosity'
info_2017 = {'file': _1_data_file, 'info': '2017_blm'}
info_2016 = {'file': _2_data_file, 'info': '2016_blm'}
#
fig = year_compare(info_2017,info_2016,normalizer)
fig.savefig(os.path.join(PLOT_DIR,'LHC_ratio','ratio_2017_2016_IP5.pdf'))
fig.savefig(os.path.join(PLOT_DIR,'LHC_ratio','ratio_2017_2016_IP5.png'))
#
#
#
_1_data_file = 'n_int_TID2017-05-01_2017-10-15_dcum_19590_20400.txt'
_2_data_file = 'n_int_TID2016-04-03_2016-10-30_dcum_19590_20400.txt'

normalizer = 'intensity'
info_2017 = {'file': _1_data_file, 'info': '2017_blm'}
info_2016 = {'file': _2_data_file, 'info': '2016_blm'}
#
fig = year_compare(info_2017,info_2016,normalizer)
fig.savefig(os.path.join(PLOT_DIR,'LHC_ratio','ratio_2017_2016_IP7.pdf'))
fig.savefig(os.path.join(PLOT_DIR,'LHC_ratio','ratio_2017_2016_IP7.png'))



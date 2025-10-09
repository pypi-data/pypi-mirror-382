import matplotlib as mpl
import matplotlib.pyplot as plt

default_options = {
        'font_size': 16, # pt
        'plot_size': (6.4, 4.8),
        'line_width': 2.5,
        'xtick_size': 13.5,
        'ytick_size': 13.5,
        }

__dc_options = {}

def init_plots_for_paper(options=default_options):
    global __dc_options
    __dc_options.update(options)
    mpl.rcParams.update({'font.size': options['font_size'], 'figure.figsize': options['plot_size'], 'lines.linewidth': options['line_width'], 'xtick.labelsize': options['xtick_size'], 'ytick.labelsize': options['ytick_size'], })
    mpl.interactive(False)

def init_plot(size=(1,1), square=False):
    global __dc_options
    fig, ax = plt.subplots(size[0], size[1])
    fig.set_tight_layout(True)
    fig.set_figwidth(__dc_options['plot_size'][0])# * size[0])
    fig.set_figheight(__dc_options['plot_size'][1])# * size[1])
    if(square):
        fig.set_figheight(__dc_options['plot_size'][0])# * size[0])
    return fig, ax


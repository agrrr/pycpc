import pandas as pd
#import seaborn as sns

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib import ticker, patches

from math import ceil

def setup_subplots(amount: int, ncols=2):
    # TODO: nrows and ncols arguments are overriden later on,
    # need to decide on what we want to have here.

    # TODO: amount, nrows, ncols must be int - need to assert
    amount = int(amount)
    ncols = int(ncols)

    subplots_shape = {4: (2,2)}
    shape = subplots_shape.pop(amount, None)
    if shape is None:
        nrows = ceil(amount/ncols)
        shape = (nrows, ncols)
    fig, axs = plt.subplots(nrows = shape[0], ncols=shape[1])
    axs = axs.flatten()

    # Delete redundant axes
    if (amount % ncols) > 0:
        to_delete_start = amount - ncols + (amount % ncols) + 1
        for i in range(to_delete_start, amount + 1):
            fig.delaxes(axs[i])
        axs = axs[:to_delete_start]
    
    fig.set_tight_layout(True)
    fig.set_size_inches(shape[1] * 5, shape[0] * 5)
    return fig, axs

def customize_ax(ax: matplotlib.axes.Axes,
                 title=None,
                 xlabel=None, ylabel=None,
                 xlim=None, ylim=None, 
                 invert_yaxis=False,
                 xticks_maj_freq=None, xticks_min_freq=None, yticks_maj_freq=None, yticks_min_freq=None, 
                 with_hline=False, hline_height=None, hline_color='r', hline_style='--'):
    """
    : ax (matplotlib.axes.Axes): plot to customize.
    : Use to customize a plot with labels, ticks, etc.
    """
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)

    if invert_yaxis:
        ax.invert_yaxis()

    if title is not None:
        ax.set_title(title)

    if xticks_maj_freq is not None:
        ax.xaxis.set_major_locator(ticker.MultipleLocator(xticks_maj_freq))
    
    if xticks_min_freq is not None:
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(xticks_min_freq))
    
    if yticks_maj_freq is not None:
        ax.yaxis.set_major_locator(ticker.MultipleLocator(yticks_maj_freq))
    
    if yticks_min_freq is not None:
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(yticks_min_freq))

    if with_hline:
        if hline_height is None:
            ylim = plt.ylim()
            hline_height = max(ylim) / 2
        ax.axhline(y=hline_height, color=hline_color, linestyle=hline_style)

    
def plot_stem(series: pd.Series, ax=None, show=False,
             title=None, xlabel=None, ylabel=None,
             xlim=None, ylim=None, 
             xticks_maj_freq=None, xticks_min_freq=None, yticks_maj_freq=None, yticks_min_freq=None, 
             with_hline=False, hline_height=None, hline_color='r', hline_style='--'):
    """
    : series (pd.Series): series.index  specifies x values 
    :                     series.values specifies y values
    : stem plot with optional horizontal line
    """
    if ax is None:
        fig, ax = plt.subplots()
    ax.stem(series.index, series.values)
    
    if xlabel is None:
        if (series.index.name is not None):
            xlabel = series.index.name

    if ylabel is None:
        if (series.name is not None):
            ylabel = series.name

    if title is None:
        title = '{y} by {x}'.format(y=ylabel, x=xlabel)

    customize_ax(ax=ax, title=title,
                 xlabel=xlabel, ylabel=ylabel,
                 xlim=xlim, ylim=ylim,
                 xticks_maj_freq=xticks_maj_freq, xticks_min_freq=xticks_min_freq,
                 yticks_maj_freq=yticks_maj_freq, yticks_min_freq=yticks_min_freq,
                 with_hline=with_hline, hline_height=hline_height,
                 hline_color=hline_color, hline_style=hline_style)    
    if show:
        plt.show()
    return ax

def plot_bar(series: pd.Series, ax=None, show=False,
             title=None, xlabel=None, ylabel=None,
             xlim=None, ylim=None, 
             xticks_maj_freq=None, xticks_min_freq=None, yticks_maj_freq=None, yticks_min_freq=None, 
             with_hline=False, hline_height=None, hline_color='r', hline_style='--'):
    """
    : series (pd.Series): series.index  specifies x values 
    :                     series.values specifies y values
    : Bar plot with optional horizontal line
    """
    plt.style.use('default')
    if ax is None:
        fig, ax = plt.subplots()
    barlist = ax.bar(series.index, series.values) # We return this for further customization 
    
    customize_ax(ax=ax, title=title,
                 xlabel=xlabel, ylabel=ylabel,
                 xlim=xlim, ylim=ylim,
                 xticks_maj_freq=xticks_maj_freq, xticks_min_freq=xticks_min_freq,
                 yticks_maj_freq=yticks_maj_freq, yticks_min_freq=yticks_min_freq,
                 with_hline=with_hline, hline_height=hline_height,
                 hline_color=hline_color, hline_style=hline_style) 
    
    if show:
        plt.show()
    return (ax, barlist)

def plot_bar_prob_by_bit_pos(series: pd.Series, r: int, ax=None, show=False,
                             title=None, xlabel='bit', ylabel='P(flip)', xlim=None, ylim=(0,1),
                             xticks_maj_freq=5, xticks_min_freq=1, yticks_maj_freq=0.2, yticks_min_freq=0.05, 
                             info_color='blue', rdnc_color='green',
                             legend_loc='upper left', legend_info_label = 'Information bits', legend_rdnc_label = 'Redundancy bits', 
                             with_hline=False, hline_height=0.5, hline_color='r', hline_style='--'):
    """
    : series (pd.Series): series.index  specifies x values 
    :                     series.values specifies y values
    : r (int): redundancy bit index
    : Bar plot a probability[not distribution] series where x-axis represents bits of a code word.
    :  > different coloring of info bits and redundancy bits.
    :  > Add horizontal line at 0.5
    """
    if xlim is None:
        xlim = (0, len(series))

    ax, barlist = plot_bar(series, ax=ax, show=False,
                                title=title, xlabel=xlabel, ylabel=ylabel,
                                xlim=xlim, ylim=ylim,
                                xticks_maj_freq=xticks_maj_freq, xticks_min_freq=xticks_min_freq,
                                yticks_maj_freq=yticks_maj_freq, yticks_min_freq=yticks_min_freq,
                                with_hline=with_hline, hline_height=hline_height,
                                hline_color=hline_color, hline_style=hline_style)
    for bl in barlist[:-r]:
        bl.set_color(info_color)
    for bl in barlist[-r:]:
        bl.set_color(rdnc_color)
    
    info_patch = patches.Patch(color=info_color, label=legend_info_label)
    rdnc_patch = patches.Patch(color=rdnc_color, label=legend_rdnc_label)
    
    ax.legend(loc=legend_loc, handles=[info_patch, rdnc_patch])
    if show:
        plt.show()
    return ax

def plot_heatmap_prob(matrix, log_scale=False, ax=None, show=False, 
                 vmin=0, vmax=1, cmap=None,
                 cbar_label = '',
                 title=None,
                 xlabel=None, ylabel=None,
                 xlim=None, ylim=None, 
                 invert_yaxis=True,
                 xticks_maj_freq=None, xticks_min_freq=None, yticks_maj_freq=None, yticks_min_freq=None):
    if ax is None:
        fig, ax = plt.subplots()
  #  if log_scale:
   #     sns.heatmap(matrix.apply(lambda x: x+1), norm=LogNorm(vmin=1, vmax=matrix.max().max()), ax=ax)
    #else:
     #   sns.heatmap(matrix, ax=ax, vmin=vmin, vmax=vmax, cmap=cmap, mask = matrix.isna(), cbar_kws={'label': cbar_label}) # TODO: allow customization of vmin, vmax
        ax.set_facecolor("#8ff7e1")

    # TODO: Support values in cell display option
    customize_ax(ax=ax, invert_yaxis=invert_yaxis,
                 title=title,
                 xlabel=xlabel, ylabel=ylabel,
                 xlim=xlim, ylim=ylim, 
                 xticks_maj_freq=xticks_maj_freq, xticks_min_freq=xticks_min_freq,
                 yticks_maj_freq=yticks_maj_freq, yticks_min_freq=yticks_min_freq)    
    if show:
        plt.show()
    return ax

def co_occurence_heatmap(attacks, keys, show_numbers=False):
    if(len(keys) != 2):
        raise Exception('Only 2 keys are allowed for co_occurence_heatmap')
    co_occurence_matrix = pd.crosstab(attacks[keys[0]], attacks[keys[1]], dropna=False)
    #if show_numbers:
     #   sns.heatmap(co_occurence_matrix, annot=True, fmt="d", linewidths=.1)
    #else:
     #   sns.heatmap(co_occurence_matrix)
    plt.gca().invert_yaxis()    
    #plt.show()

def sort_multindex(df):
    sorted_indexes = df.index.to_frame().reset_index(drop=True).apply(pd.Series.nunique).sort_values().index.to_list()
    return df.reorder_levels(sorted_indexes)
    # TODO better place for it
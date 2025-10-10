from typing import List, Tuple, Union, Iterable, Dict, Any
import matplotlib.pyplot as plt

from cooptools.colors import Color
import cooptools.os_manip as osm
import os
import numpy as np
import logging
from dataclasses import dataclass

cmap = plt.cm.RdYlGn
norm = plt.Normalize(1, 4)


@dataclass(frozen=True, slots=True)
class PlotArgs:
    color: Color = None
    linestyle: str = None
    linewidth: float = None
    labels: Dict[Any, str] = None #expect to supply the x-value as the key, label as the str



# https://stackoverflow.com/questions/7908636/how-to-add-hovering-annotations-to-a-plot
def update_scatter_annot(ind, annot, sc, labels):
    c = np.random.randint(1, 5, size=len(labels))
    pos = sc.get_offsets()[ind["ind"][0]]
    annot.xy = pos
    # text = "{}, {}".format(" ".join(list(map(str, ind["ind"]))),
    #                        " ".join([labels[n] for n in ind["ind"]]))
    text = " ".join([str(labels[n]) for n in ind["ind"]])

    annot.set_text(text)
    annot.get_bbox_patch().set_facecolor(cmap(norm(c[ind["ind"][0]])))
    annot.get_bbox_patch().set_alpha(0.4)





def scatter_hover(event, annot, ax, fig, sc, labels):
    vis = annot.get_visible()
    if event.inaxes == ax:
        cont, ind = sc.contains(event)
        if cont:
            update_scatter_annot(ind, annot, sc=sc, labels=labels)
            annot.set_visible(True)
            fig.canvas.draw_idle()
        else:
            if vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()


def plot_series(points: List[Tuple[float, float]],
                ax,
                fig,
                color: Union[Color, Tuple[float, float, float]] = None,
                series_type=None,
                label=None,
                line_width: int = None,
                line_style: str = None,
                point_size=None,
                y_bounds=None,
                zOrder: int = None,
                labels: Iterable[str] = None,
                show_all_labels: bool = False):
    """

    :param points:
    :param ax:
    :param color:
    :param series_type:
    :param label:
    :param line_width:
    :param line_style: [‘solid’, ‘dashed’, ‘dashdot’, ‘dotted’, (offset, on-off-dash-seq), '-', '--', '-.', ':', 'None', ' ', '']
    :return:
    """

    if points is None or len(points) == 0:
        return

    res = list(zip(*points))

    if type(color) == Color:
        color = tuple([x / 255 for x in color.value])

    if series_type is None or series_type in ['line']:
        if zOrder is None: zOrder = 2
        ax.plot(res[0], res[1], color=color, linewidth=line_width, label=label, linestyle=line_style, zorder=zOrder)
        ax.text((res[0][0] + res[0][-1]) // 2, (res[1][0] + res[1][-1]) // 2, label)
    elif series_type == 'scatter':
        if zOrder is None: zOrder = 3
        sc = ax.scatter(res[0], res[1], color=color, label=label, s=point_size, zorder=zOrder)

        if labels is not None and show_all_labels:
            for i, pt in enumerate(points):
                ax.annotate(labels[i], (pt[0], pt[1]))

        if labels is not None and not show_all_labels:
            annot = ax.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
                                bbox=dict(boxstyle="round", fc="w"),
                                arrowprops=dict(arrowstyle="->"))

            annot.set_visible(False)
            fig.canvas.mpl_connect("motion_notify_event", lambda event: scatter_hover(event, annot, ax, fig, sc, labels=labels))
    elif series_type == 'fill':
        if zOrder is None: zOrder = 1
        ax.fill(res[0], res[1], color=color, zorder=zOrder)
    elif type == 'pie':
        ax.pie(y='mass', figsize=(5, 5))
    else:
        raise TypeError(f"type {series_type} is unknown")


def calc_ylims(df, bounds_specified):
    if bounds_specified[0] is not None:
        y_lim_low = bounds_specified[0]
    else:
        y_lim_low = df.select_dtypes(include=[np.number]).min().min()
        if y_lim_low < 0:
            y_lim_low = y_lim_low * 1.15
        else:
            y_lim_low = y_lim_low * 0.85

    if bounds_specified[1] is not None:
        y_lim_high = bounds_specified[1]
    else:
        y_lim_high = df.select_dtypes(include=[np.number]).max().max()
        if y_lim_high < 0:
            y_lim_high = y_lim_high * 0.85
        else:
            y_lim_high = y_lim_high * 1.15

        if y_lim_high == y_lim_low: y_lim_high = y_lim_low + 1

    return y_lim_low, y_lim_high


def autopct_generator(limit):
    def inner_autopct(pct):
        return f"{('%.1f' % pct)}%" if pct > limit else ''

    return inner_autopct


def show_and_save_plot(fig: plt.Figure,
                       title="[Title]",
                       saveloc=None,
                       show_fig: bool = True):
    ''' Plots a figure and saves it to a provided output location'''

    '''
    Tight layout often produces nice results
    but requires the title to be spaced accordingly
    https://stackoverflow.com/questions/7066121/how-to-set-a-single-main-title-above-all-the-subplots-with-pyplot/35676071
    '''
    fig.suptitle(title, fontsize=24)
    fig.tight_layout()
    fig.subplots_adjust(top=0.88)

    '''
    Must save the file before the plt.show() call, otherwise the reference fails
    '''
    if saveloc:
        osm.check_and_make_dirs(os.path.dirname(saveloc))
        fig.savefig(saveloc)
        logging.info(f"figure saved to {saveloc}")

    ''' Show the plot'''
    if show_fig:
        plt.show()


def plot_datetime(df,
                  ax: plt.Axes,
                  title=None,
                  type=None,
                  xaxis=None,
                  highlight=True,
                  weekend=5,
                  ylabel=None,
                  facecolor='green',
                  alpha_span=0.2,
                  linestyle='-',
                  y_bounds=None,
                  x_label_rot=None):
    """
    Draw a plot of a dataframe
    df(pandas) = pandas dataframe
    highlight(bool) = to highlight or not
    title(string) = title of plot
    saveloc(string) = where to save file
    """

    if type is None:
        type = 'line'

    if xaxis is None:
        df['_tmp_'] = df.index
        xaxis = '_tmp_'

    # draw all columns of dataframe
    for v in df.columns.tolist():
        if v != xaxis:
            df.plot(x=xaxis, y=v, kind=type, ax=ax, linestyle=linestyle)

    # if highlight:
    #     # find weekend indeces
    #     weekend_indices = find_weekend_indices(df.index, weekend=5)
    #     # highlight weekends
    #     highlight_datetimes(weekend_indices, axes, df, facecolor)

    # set y label
    if ylabel:
        ax.set_ylabel(ylabel)

    ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0))
    plt.tight_layout()
    if title:
        ax.set_title(title)

    if y_bounds:
        ax.set_ylim(calc_ylims(df, y_bounds))

    # add xaxis gridlines
    ax.xaxis.grid(b=True, which='major', color='black', linestyle='--', alpha=1)

    if x_label_rot:
        ax.tick_params(axis='x', labelrotation=x_label_rot)

    return ax


def fix_labels(mylabels, tooclose=0.1, sepfactor=2):
    vecs = np.zeros((len(mylabels), len(mylabels), 2))
    dists = np.zeros((len(mylabels), len(mylabels)))
    for i in range(0, len(mylabels) - 1):
        for j in range(i + 1, len(mylabels)):
            a = np.array(mylabels[i].get_position())
            b = np.array(mylabels[j].get_position())
            dists[i, j] = np.linalg.norm(a - b)
            vecs[i, j, :] = a - b
            if dists[i, j] < tooclose:
                mylabels[i].set_x(a[0] + sepfactor * vecs[i, j, 0])
                mylabels[i].set_y(a[1] + sepfactor * vecs[i, j, 1])
                mylabels[j].set_x(b[0] - sepfactor * vecs[i, j, 0])
                mylabels[j].set_y(b[1] - sepfactor * vecs[i, j, 1])
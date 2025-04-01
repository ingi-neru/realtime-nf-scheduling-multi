#!/usr/bin/env python3
""" Plot RT Cloud Simulator data. """

import argparse

import matplotlib.pyplot as plt
from numpy import datetime_as_string
import pandas as pd

plt.set_loglevel("warning")

def get_flowid_from_column(column_name: str, column_type: str) -> str:
    """ Collect flow ID from a column name (e.g., delay[0] -> 0).

    Parameters:
    column_name (str): Full name of a dataframe column
    column_type (str): Type of the column (rate, delay, etc.), a substring of column_name

    Returns:
    flow ID as a string
    """
    return column_name.replace("_slo", '').replace(f"{column_type}[", '').replace(']', '')


def plot_csv(csv_file: str, title=None, outfile=None, tasks=None, flows=None):

    """ Plot simulator CSV data.

    Parameters:
    csv_file (str): input CSV file path
    title (str): plot title
    outfile (str/None): write graph to this PNG file; show plot if set to None
    tasks (list/None): names of tasks to plot
    flows (list/None): names of flows to plot
    """
    _dataframe = pd.read_csv(csv_file)
    print("outfile = ", outfile)
    plot_df(_dataframe, title, outfile, tasks, flows)


def plot_df(df: pd.DataFrame, title=None, outfile=None, tasks=None, flows=None):
    """Plot simulator data from a Pandas Dataframe. Either write to file
    or show plot.

    Parameters:
    df (pandas.DataFrame): input dataframe
    title (str): plot title
    outfile (str/None): write graph to this PNG file; show plot if set to None
    tasks (list/None): names of tasks to plot
    flows (list/None): names of flows to plot
    """
    flow_names = flows or [""]
    task_names = tasks or [""]
    flow_columns = [c for c in df.columns if any(f in c for f in flow_names)]
    task_columns = [c for c in df.columns if any(t in c for t in task_names)]

    plt.style.use('seaborn-v0_8-colorblind')
    size = 12.5
    params = {'legend.fontsize': 'large',
              'axes.labelsize': size,
              'axes.titlesize': size,
              #'figure.titlesize': size*1.375,
              'figure.titlesize': size*1.1,
              'xtick.labelsize': size*0.75,
              'ytick.labelsize': size*0.75,
              'axes.titlepad': size*1.25}
    plt.rcParams.update(params)
    marker_size = 5

    fig, axes = plt.subplots(4, 1,
                             #figsize=(15, 10.5),
                             figsize=(9, 9),
                             sharex=True,
                             )

    num_plot_lines = []
    # rate
    columns_to_plot = [c for c in df.columns if "rate" in c and c in flow_columns]
    num_plot_lines.append(len(columns_to_plot))
    for y_ax in columns_to_plot:
        flow_id = get_flowid_from_column(y_ax, "rate")
        legend_label = f"{flow_id}"
        marker = 'o'
        if "slo" in y_ax:
            legend_label += " (SLO)"
            marker = ''
        df.plot(
            ax=axes[0],
            marker=marker,
            ms=marker_size,
            y=y_ax,
            label=legend_label,
        )
    axes[0].set_title('Flow Rates')
    axes[0].set_xlabel('Time [round]')
    axes[0].set_ylabel('Rate')

    # delay
    columns_to_plot = [c for c in df.columns if "delay" in c and c in flow_columns]
    num_plot_lines.append(len(columns_to_plot))
    for y_ax in columns_to_plot:
        flow_id = get_flowid_from_column(y_ax, "delay")
        legend_label = f"{flow_id}"
        marker = 'X'
        if "slo" in y_ax:
            legend_label += " (SLO)"
            marker = ''
        df.plot(
            ax=axes[1],
            marker=marker,
            ms=marker_size,
            y=y_ax,
            label=legend_label,
        )
    axes[1].set_title('Flow Delays')
    axes[1].set_ylabel('Flow Delay')

    # weight
    columns_to_plot = [c for c in df.columns if "weight" in c and c in task_columns]
    num_plot_lines.append(len(columns_to_plot))
    for y_ax in columns_to_plot:
        legend_label = y_ax.replace("weight[", '').replace(']', '')
        df.plot(
            ax=axes[2],
            marker='D',
            ms=marker_size,
            y=y_ax,
            label=legend_label,
        )
    axes[2].set_title('Task Weights')
    axes[2].set_ylabel('Weight')
    axes[2].set_xlabel('Time [round]')

    # lambda
    columns_to_plot = [c for c in df.columns if "lambda" in c and c in task_columns]
    num_plot_lines.append(len(columns_to_plot))
    markers = ['D', 'P', 'X', '*', 'p', 'o', 'H']
    base_alpha = .9
    for mark_idx, y_ax in enumerate(columns_to_plot):
        legend_label = y_ax.replace("lambda[", '').replace(']', '')
        df.plot(
            ax=axes[3],
            linewidth=.75,
            alpha=base_alpha - (mark_idx * .05),
            marker=markers[mark_idx % len(markers)],
            ms=marker_size*1.8,
            y=y_ax,
            label=legend_label,
        )

    axes[3].set_title('Task Lambdas')
    axes[3].set_ylabel('Lambda')
    axes[3].set_xlabel('Time [round]')
    axes[3].set_yticks([0, 1])
    axes[3].set_ylim(-.1, 1.1)
    axes[3].set_xticks(range(0, len(df.index)))
    # show xticklabels for every 5th xtick
    xticks = axes[3].xaxis.get_major_ticks()
    for i, tick in enumerate(xticks):
        if i % 5 != 0:
            tick.label1.set_visible(False)

    # set number of legend columns based on the number of lines to plot:
    # aim for 6 rows per column, but max 3 columns
    num_legend_cols = min(max(max(num_plot_lines) // 6, 1), 3)

    for ax in axes:
        ax.legend(
            ncol=num_legend_cols,
            loc="center left",
            bbox_to_anchor=(1, .5),
        )

    # set title
    if title:
        fig.suptitle(title)

    # set layout
    layout_args = {}
    if title:
        layout_args['rect'] = [0, 0, 1, .95]
    plt.tight_layout(**layout_args)

    # present figure
    print('outfile = ', outfile)
    if outfile:
        plt.savefig(outfile, dpi=150)
    else:
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('csvfile', type=argparse.FileType('r'),
                        help='csv to show')
    parser.add_argument("-o", "--outfile", type=str,
                        help="File to save plot")
    parser.add_argument("-t", "--title", type=str,
                        help="Plot title", default='')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose mode')
    args = parser.parse_args()

    dataframe = pd.read_csv(args.csvfile)

    if args.verbose:
        print(dataframe)

    # plot figure
    plot_df(dataframe, args.title, args.outfile)

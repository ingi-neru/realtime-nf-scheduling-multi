#! /usr/bin/env python3
""" Plot dtf-estimate-check.bess measurement results. """

import argparse

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

size = 12
params = {'legend.fontsize': size,
          'axes.labelsize': size,
          'axes.titlesize': size,
          'xtick.labelsize': size*0.75,
          'ytick.labelsize': size*0.75,
          'axes.titlepad': size*0.25, }
plt.rcParams.update(params)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file", type=str, default=".",
                        help="CSV file to read")
    parser.add_argument("-o", "--outfile", type=str,
                        help="File to write plot")
    args = parser.parse_args()

    df = pd.read_csv(args.csv_file, index_col=False, header=0, sep='\t')

    cycle_nums = list(set(df['task1_cycle_num'].to_list()))
    cycle_nums.sort()

    if args.outfile:
        plt.switch_backend('Agg')

    task_names = set(c[:5] for c in df.columns if "task" in c)
    num_tasks = len(task_names)

    _, axes = plt.subplots(num_tasks, len(cycle_nums),
                           # sharey=True,
                           # sharex=True,
                           figsize=(20, 12))

    columns = ("50",
               "90",
               "95",
               "99",
               # "max",
               "est",
               )

    columns_to_plot = [[f"task{i+1}_{c}" for c in columns]
                       for i in range(num_tasks)]

    colors = [
        "slateblue", "magenta", "darkgoldenrod", "chocolate", "firebrick", "black"
    ]

    # task1: varying params
    for i, cycle_num in enumerate(cycle_nums):
        df_filtered = df[df['task1_cycle_num'] ==
                         cycle_nums[i]].sort_values(by=['task1_weight'])
        for color_idx, y_ax in enumerate(columns_to_plot[0]):
            mark = "p"
            if "fast" in y_ax:
                mark = "o"
            if "est" in y_ax:
                if "fast" in y_ax:
                    mark = "s"
                else:
                    mark = "D"
                if "old" in y_ax:
                    mark = "*"
                    if "fast" in y_ax:
                        mark = "X"

            df_filtered.plot(ax=axes[0, i],
                             marker=mark,
                             x='task1_weight',
                             y=y_ax,
                             color=colors[color_idx % len(colors)],
                             # loglog=True,
                             logy=True,
                             legend=False,
                             subplots=True)

            axes[0, i].set_title(f"Task1: {cycle_num} [cycles]")
            axes[0, i].set_xlabel("Task1 Weight")

            axes[0, i].set_xticks(df_filtered['task1_weight'])
            axes[0, i].set_xticklabels(axes[0, i].get_xticks(), rotation=45)
            axes[0, i].get_xaxis().set_major_formatter(
                matplotlib.ticker.FuncFormatter(lambda x, y: f"{x/1024:.2f}"))
    axes[0, 0].set_ylabel("Task1 Delay/Estimate [ns]")

    # task2: fix
    for i, cycle_num in enumerate(cycle_nums):
        df_filtered = df[df['task1_cycle_num'] ==
                         cycle_nums[i]].sort_values(by=['task2_weight'])
        for color_idx, y_ax in enumerate(columns_to_plot[1]):
            mark = "p"
            if "fast" in y_ax:
                mark = "o"
            if "est" in y_ax:
                if "fast" in y_ax:
                    mark = "s"
                else:
                    mark = "D"
                if "old" in y_ax:
                    mark = "*"
                    if "fast" in y_ax:
                        mark = "X"

            df_filtered.plot(ax=axes[1, i],
                             marker=mark,
                             x='task2_weight',
                             y=y_ax,
                             color=colors[color_idx % len(colors)],
                             # loglog=True,
                             logy=True,
                             legend=False,
                             subplots=True)

            axes[1, i].invert_xaxis()

            #axes[1, i].set_title(f"Task2: {cycle_num} [cycles]")
            axes[1, i].set_xlabel("Task2 Weight")

            axes[1, i].set_xticks(df_filtered['task2_weight'])
            axes[1, i].set_xticklabels(axes[1, i].get_xticks(), rotation=45)
            axes[1, i].get_xaxis().set_major_formatter(
                matplotlib.ticker.FuncFormatter(lambda x, y: f"{x/1024:.2f}"))
        axes[1, 0].set_ylabel("Task2 Delay/Estimate [ns]")

    # task3: fix
    if num_tasks == 3:
        for i, cycle_num in enumerate(cycle_nums):
            df_filtered = df[df['task1_cycle_num'] ==
                             cycle_nums[i]].sort_values(by=['task3_weight'])
            for color_idx, y_ax in enumerate(columns_to_plot[2]):
                mark = "p"
                if "fast" in y_ax:
                    mark = "o"
                if "est" in y_ax:
                    if "fast" in y_ax:
                        mark = "s"
                    else:
                        mark = "D"
                    if "old" in y_ax:
                        mark = "*"
                        if "fast" in y_ax:
                            mark = "X"

                df_filtered.plot(ax=axes[2, i],
                                 marker=mark,
                                 x='task3_weight',
                                 y=y_ax,
                                 color=colors[color_idx % len(colors)],
                                 # loglog=True,
                                 logy=True,
                                 legend=False,
                                 subplots=True)

                axes[2, i].invert_xaxis()

                #axes[2, i].set_title(f"Task2: {cycle_num} [cycles]")
                axes[2, i].set_xlabel("Task3 Weight")

                axes[2, i].set_xticks(df_filtered['task3_weight'])
                axes[2, i].set_xticklabels(axes[2, i].get_xticks(),
                                           rotation=45)
                axes[2, i].get_xaxis().set_major_formatter(
                    matplotlib.ticker.FuncFormatter(lambda x, y: f"{x/1024:.2f}"))
            axes[2, 0].set_ylabel("Task3 Delay/Estimate [ns]")

    for main_axes in axes:
        ax_last = main_axes[-1]
        ax_last.legend(
            ncol=1,
            loc="center left",
            bbox_to_anchor=(1, .5),
        )

    # set layout
    layout_args = {'h_pad': 3, 'w_pad': -.5}
    plt.tight_layout(**layout_args)

    # present figure
    if args.outfile:
        plt.savefig(args.outfile, dpi=150)
    else:
        plt.show()

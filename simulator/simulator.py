#!/usr/bin/env python3
""" RT Switch Simulator """

import argparse
import configparser
import logging
import sys

import networkx as nx

from lib import settings
from lib import simulator as sim
from lib import utils
from plot_results import plot_csv


def get_logging_level_names():
    """ Get logging level names """
    #pylint: disable=W0212
    level_names = logging._levelToName
    return [logging.getLevelName(x) for x in level_names]


if __name__ == "__main__":
    #pylint: disable=C0103
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', type=str, default='',
                        help='Config file to read')
    parser.add_argument('--rounds', '-r', type=int,
                        default=settings.DEFAULT_SIMULATION_ROUNDS,
                        help='Number of optimization rounds')
    parser.add_argument('--realloc_interval', '-ri', type=int,
                        default=settings.DEFAULT_REALLOC_CONTROLLER_INTERVAL,
                        help='Interval (rounds) between to Resource Reallocation')
    parser.add_argument('--rho_roughness', '-R', type=float,
                        default=settings.DEFAULT_RHO_ROUGHNESS,
                        help='Rho Roughness')
    parser.add_argument('--epsilon', '-e', type=float,
                        default=settings.DEFAULT_EPSILON,
                        help='Epsilon')
    parser.add_argument('--delta', '-d', type=float,
                        default=settings.DEFAULT_DELTA,
                        help='Delta')
    parser.add_argument('--alpha', '-a', type=float,
                        default=settings.DEFAULT_ALPHA,
                        help='Alpha')
    parser.add_argument('--loglevel', '-l', type=str,
                        default='INFO', choices=get_logging_level_names(),
                        help='Loglevel')
    parser.add_argument('--infile', '-i', type=str,
                        help='Input GML file')
    parser.add_argument('--outfile', '-o', type=str,
                        default=settings.DEFAULT_OUTFILE,
                        help='Output CSV file')
    parser.add_argument('--plot_flows', '-f', type=str, nargs='*',
                        help='Flows to plot (e.g., "Flow 0" "Flow 1")')
    parser.add_argument('--plot_tasks', '-t', type=str, nargs='*',
                        help='Tasks to plot (e.g., "Task 0" "Task 1")')
    parser.add_argument('--plot', '-p', action='store_true',
                        help='Enable plotting')
    parser.add_argument('--plotfile', '-P', type=str, default='',
                        help='Plot file (PNG, PDF works)')
    args_parsed = parser.parse_args()

    if args_parsed.config:
        # read config file
        config = configparser.ConfigParser()
        config.read(args_parsed.config)

        # collect parameters from the config file
        try:
            input_file = config['pipeline']['file']
        except KeyError as e:
            err_txt = f'Missing input file config. Set pipeline/file in {args_parsed.config}'
            raise ValueError(err_txt) from e
        __w_list = config['pipeline']['weights'].replace(' ', '').split(',')
        w = [float(x)
             for x in __w_list]
        sim_rounds = int(config['simulator'].get('rounds', 20))
        realloc_int = int(config['simulator'].get('realloc_interval',
                                                  settings.DEFAULT_REALLOC_CONTROLLER_INTERVAL))
        _sim_params = {
            'alpha': config['simulator'].get('alpha', settings.DEFAULT_ALPHA),
            'delta': config['simulator'].get('delta', settings.DEFAULT_DELTA),
            'rho_roughness': config['simulator'].get('rho_roughness',
                                                     settings.DEFAULT_RHO_ROUGHNESS),
            'eps': config['simulator'].get('epsilon', settings.DEFAULT_EPSILON),
            'realloc_interval': realloc_int,
        }
        simulator_params = {k: float(v) for k, v in _sim_params.items()}

        __flows_plot_config = config['plot'].get('flows', None)
        flows_to_plot = __flows_plot_config
        if __flows_plot_config:
            flows_to_plot = __flows_plot_config.split(',')

        __tasks_plot_config = config['plot'].get('tasks', None)
        tasks_to_plot = __tasks_plot_config
        if __tasks_plot_config:
            tasks_to_plot = __tasks_plot_config.split(',')

        out_file = config['simulator'].get('outfile', settings.DEFAULT_OUTFILE)
        plot_file = config['plot'].get('file', '')

        loglevel = config['simulator'].get('loglevel', 'INFO')

    else:
        input_file = args_parsed.infile
        if not input_file:
            raise ValueError('Missing input file argument. Use --infile <file>')

        # guess weight
        w = utils.guess_task_weights(input_file)

        sim_rounds = args_parsed.rounds
        simulator_params = {
            'alpha': args_parsed.alpha,
            'delta': args_parsed.delta,
            'rho_roughness': args_parsed.rho_roughness,
            'eps': args_parsed.epsilon,
            'realloc_interval': args_parsed.realloc_interval,
        }

        flows_to_plot = args_parsed.plot_flows
        tasks_to_plot = args_parsed.plot_tasks

        out_file = args_parsed.outfile
        plot_file = args_parsed.plotfile

        loglevel = args_parsed.loglevel

    # set loglevel
    logging.basicConfig(stream=sys.stdout,
                        level=getattr(logging, str(loglevel)),
                        format='%(message)s')

    # init simulator
    G = nx.read_gml(input_file)
    simulator = sim.Simulator(simulator_params=simulator_params)
    simulator.init_from_gml(G, w)

    # run simulator
    simulator.run_simulation(rounds=sim_rounds)

    # write results
    simulator.write_results(out_file)

    # plot results
    if args_parsed.plot:
        plot_title = (f"{simulator.name} "
                      f"(alpha={simulator_params['alpha']}, "
                      f"delta={simulator_params['delta']}, "
                      f"step_size={simulator_params['rho_roughness']}, "
                      f"epsilon={simulator_params['eps']})")
        plot_args = {
            'title': plot_title,
            'csv_file': out_file,
            'flows': flows_to_plot,
            'tasks': tasks_to_plot,
        }
        if args_parsed.plotfile:
            plot_args['outfile'] = plot_file
        plot_csv(**plot_args)

    logging.log(logging.INFO, "\nThat's all, folks!")

import itertools
import logging

import numpy as np

from . import settings


class Singleton(type):
    """ Singleton class based on https://stackoverflow.com/q/6760685 """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def pairwise(iterable):
    """ Return successive overlapping pairs taken from the input iterable

    Example: pairwise('ABCDEFG') --> AB BC CD DE EF FG
    Taken from https://docs.python.org/3.10/library/itertools.html
    """
    #pylint: disable=C0103
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def get_default_slo_params():
    """ Returns default SLO parameters. """
    return {'rate': settings.DEFAULT_RATE_SLO,
            'delay': settings.DEFAULT_DELAY_SLO}


def get_default_switch_params():
    """ Returns default switch parameters. """
    return {'queue_size': settings.DEFAULT_QUEUE_SIZE,
            'batch_size': settings.DEFAULT_BATCH_SIZE}


def guess_task_weights(filename):
    """ Guess task weights in the known scenarios"""
    if 'example_basic' in filename:
        if 'fixed' in filename:
            return [0.005, 0.005, 0.78, 0.21]
        return [0.333, 0.333, 0.334]

    if 'taildrop' in filename:
        if '4' in filename:
            return [0.25, 0.25, 0.25, 0.25]
        if '7' in filename:
            return[0.142, 0.142, 0.142, 0.142, 0.142, 0.142, 0.143]
        return [0.313, 0.334, 0.353]

    if 'mgw' in filename:
        # the mgw setup: ingress, egress weight is 1,
        # bearer tasks share CPU equally
        with open(filename) as conf_file:
            mgw_tasks = set()
            for line in conf_file.readlines():
                if "task " in line:
                    mgw_tasks.add(line.strip())
            num_bearer_tasks = len(mgw_tasks)
            weight_list = [[1], [1/num_bearer_tasks] * num_bearer_tasks, [1]]
            return [e for sublist in weight_list for e in sublist]

    raise Exception("Weights cannot be set")


def project_vector(u):
    """ Project vector onto a plane
        Inspired by https://www.geeksforgeeks.org/vector-projection-using-python/
    """
    # pylint: disable=C0103
    if len(u) < 3:
        if len(u) == 1:
            logging.log(logging.DEBUG, "Dead end in projection")
            return u  # is this fine?
        if len(u) == 2:
            return ((u[0]-u[1])/2, (u[1]-u[0])/2)
    # For the cross product, the length of the vector must be 2 or 3
    logging.log(logging.DEBUG,
                "Dimension of vector to be projected: LEN u=%d", len(u))
    v1 = np.asarray([1.0, 2.0, -3.0])
    v2 = np.asarray([2.0, 0.0, -2.0])
    n_short = np.cross(v1, v2)
    n = np.zeros(len(u))
    # pylint: disable=C0200
    for i in range(len(n_short)):
        n[i] = n_short[i]
    n_norm = np.sqrt(sum(n ** 2))
    proj_of_u_on_n = (np.dot(u, n) / n_norm ** 2) * n
    return u - proj_of_u_on_n

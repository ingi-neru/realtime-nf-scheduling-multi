import numpy as np
import logging

from . import settings

class ControllerCommonFns:
    """Common controller functions for both single switch and end to end case"""

    def __repr__(self) -> str:
        return f"Common controller functions for both single switch and end to end case"
    
    @staticmethod 
    def calc_flow_delay(_worker, flow, weights):
        flow_delay = 0
        j = 0
        for _task in _worker.tasks:
            flow_delay += _task.calc_time_if_full_weight() / weights[j]
            j += 1
        for _taskflow in flow.taskflows:
            if _taskflow.task not in _worker.tasks:
                flow_delay += _taskflow.task.calc_time_if_full_weight() / _taskflow.task.weight
        return flow_delay


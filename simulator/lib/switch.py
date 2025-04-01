from . import settings
from . import utils
from . import simulator

class Switch:
    """ Represents a switch """

    def __init__(self, simulator=simulator, controller=None, flows=None, workers=None,
                 reallocation_controller=None, switch_params=None, switch_id=0):
        _sw_params = switch_params
        if switch_params is None:
            _sw_params = utils.get_default_switch_params()
        self.queue_size = _sw_params.get('queue_size', settings.DEFAULT_QUEUE_SIZE)
        self.batch_size = _sw_params.get('batch_size', settings.DEFAULT_BATCH_SIZE)
        self.switch_id = _sw_params.get('switch_id', -1)
        self.simulator = simulator
        self.controller = controller
        self.reallocation_controller = reallocation_controller
        self.flows = flows
        self.workers = workers
        self.switch_id = switch_id
    def __repr__(self):
        return f"Switch{self.get_id()}"

    def get_id(self):
        """ Get Switch ID """
        return self.switch_id

    def calc_obj_value(self):
        """ Calculate total objecive function value on switch """
        alpha = self.simulator.simulator_params['alpha']
        total_excess_delay = sum(flow.calc_excess_delay() for flow in self.flows)
        total_weighted_lambdas = 0
        for _worker in self.workers:
            for _task in _worker.tasks:
                total_weighted_lambdas += _task.lambd * _task.weight
        return alpha * total_excess_delay - total_weighted_lambdas

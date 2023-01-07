from . import utils


class Flow:
    """ Represents a flow """

    def __init__(self, rate, current_rate=0.0,
                 name=None, taskflows=None, slo_params=None, flow_id=-1):
        self.name = name or f"flow{flow_id:d}"
        self.rate = rate
        self.current_rate = current_rate
        self.slo_params = slo_params or utils.get_default_slo_params()
        self.flow_id = flow_id
        self.taskflows = taskflows or []

    def __repr__(self):
        return (f"Flow{self.get_id()} {self.name}: "
                f"rate: {self.rate}, SLOs: {self.slo_params}, "
                f"path: {self.taskflows}")

    def get_id(self):
        """ Get Flow ID """
        return self.flow_id

    def add_taskflow(self, taskflow):
        """ Add a taskflow """
        self.taskflows.append(taskflow)

    def calc_delay(self):
        """ Calculate flow delay """
        return sum(tflow.calc_delay() for tflow in self.taskflows)

    def calc_delay_margin(self):
        """ Return remaining delay budget """
        return self.slo_params['delay'] - self.calc_delay()

    def calc_excess_delay(self):
        """ Return the flow delay above the delay SLO of the flow """
        return max(0, self.calc_delay_margin())

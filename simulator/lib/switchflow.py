
class SwitchFlow:
    """ Represents a switch flow: a flow from switch input to switch output """

    def __init__(self, rate, current_rate=0.0,
                 name=None, switch=None, flow=None,
                 taskflows=None, switchflow_id=-1):
        self.name = name or f"switchflow{switchflow_id:d}"
        self.rate = rate
        self.current_rate = current_rate
        self.switchflow_id = switchflow_id
        self.switch = switch
        self.flow = flow
        self.taskflows = taskflows or []

    def __repr__(self):
        return (f"SwitchFlow{self.get_id()} {self.name}: "
                f"rate: {self.rate}, path: {self.taskflows}")

    def get_id(self):
        """ Get SwitchFlow ID """
        return self.switchflow_id

    def add_taskflow(self, taskflow):
        """ Add a taskflow """
        self.taskflows.append(taskflow)

    def calc_delay(self):
        """ Calculate switchflow delay """
        return sum(tflow.calc_delay() for tflow in self.taskflows)

from . import worker
class Task:
    """ Represents a task """

    def __init__(self, name, worker=worker, taskflows=None, weight=1.0, task_id=-1, switch_id=0):
        self.name = name
        self.worker = worker
        self.weight = weight
        self.task_id = task_id
        self.taskflows = taskflows or []
        self.switch_id = switch_id
        # lambda: 1 if task has high load, 0 otherwise
        self.lambd = 0

    def __repr__(self):
        return (f"Task{self.get_id()}: runs on Worker{self.worker.get_id()} "
                f"weight: {self.weight}, taskflows: {self.taskflows}")

    def get_id(self):
        """ Get Task ID """
        return self.task_id

    def set_weight(self, weight):
        """ Set task weight (w) """
        self.weight = weight

    def add_taskflow(self, taskflow):
        """ Register a taskflow to the task """
        self.taskflows.append(taskflow)

    def migrate_to_worker(self, worker):
        """ Migrate task from current worker to given worker
            Parameters:
            worker (Worker): new worker of the task
        """
        self.worker.detach_task(self)
        worker.add_task(self)

    def has_taskflow_with_id(self, taskflow_id):
        """ Check if task has a taskflow given by its ID """
        if not self.taskflows:
            return False
        return any(e for e in self.taskflows
                   if e.get_id() == taskflow_id)

    def get_taskflow_by_id(self, taskflow_id):
        """ Return taskflow specified by its ID or None if taskflow not found """
        return next((e for e in self.taskflows
                     if e.get_id() == taskflow_id),
                    None)

    def calc_theta(self):
        """ Calculate task theta value """
        sum_flow_rate = sum(tflow.flow.current_rate
                            for tflow in self.taskflows)
        theta = sum(tflow.flow.current_rate * tflow.calc_proc_cost()
                    for tflow in self.taskflows) / sum_flow_rate
        return theta

    def calc_load(self):
        """ Calculate task load """
        switch = self.worker.switch
        alpha = switch.simulator.simulator_params['alpha']
        queue_size = switch.queue_size
        queuing_load = queue_size / self.worker.speed
        theta = self.calc_theta()
        per_flow_loads = [(queuing_load * theta) / (tflow.slo_params['delay'] * self.weight)
                          for tflow in self.taskflows]
        sum_load = alpha * sum(per_flow_loads)
        bp_term = self.lambd * self.weight
        return sum_load - bp_term

    def calc_worker_usage(self):
        """ Calculate worker usage as the function of flow rates and processing costs """
        return sum(tflow.flow.current_rate * tflow.calc_proc_cost()
                   for tflow in self.taskflows)
    
    def calc_load_deriv(self):
        switch = self.worker.switch
        if switch.simulator.endtoend_controller:
            return self.calc_load_deriv_end_to_end()
        else:
            return self.calc_load_deriv_single_switch()

    def calc_load_deriv_single_switch(self):
        """ Calculate task load derivative """
        switch = self.worker.switch
        alpha = switch.simulator.simulator_params['alpha']
        queue_size = switch.queue_size
        theta = self.calc_theta()

        delay_violating_tflows = [tflow
                                  for tflow in self.taskflows
                                  if tflow.flow.calc_delay() > tflow.slo_params['delay']]
        _common_term = self.worker.speed * pow(self.weight, 2)
        sum_viol_flow_load = sum(theta * queue_size / _common_term
                                 for _ in delay_violating_tflows)

        return alpha * sum_viol_flow_load + self.lambd
    
    def calc_load_deriv_end_to_end(self):
        switch = self.worker.switch
        alpha = switch.simulator.simulator_params['alpha']
        queue_size = switch.queue_size
        theta = self.calc_theta()
        squared_weight = pow(self.weight, 2)
        _lambda = self.lambd

        common_term = (alpha * theta * queue_size) / sum(self.worker.speed * squared_weight * _tflow.slo_params['delay'] for _tflow in self.taskflows)
        return common_term + _lambda 

    def calc_time_if_full_weight(self):
        """ Calculate task speed if it had a weight = 1 """
        switch = self.worker.switch
        queue_size = switch.queue_size
        theta = self.calc_theta()

        return theta * queue_size / self.worker.speed

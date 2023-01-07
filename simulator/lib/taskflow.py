from . import settings


class TaskFlow:
    """ Represents a task flow: part of a flow running on a single task """

    def __init__(self, modules, task, flow, taskflow_id=-1):
        self.modules = modules
        self.task = task
        self.flow = flow
        self.slo_params = flow.slo_params
        self.taskflow_id = taskflow_id

    def __repr__(self):
        return (f"TaskFlow{self.get_id()} on Task{self.task.get_id()}: "
                f"{self.modules[0]} -> {self.modules[-1]}: "
                f"SLO params={self.slo_params}")

    def get_id(self):
        """ Get Taskflow ID """
        return self.taskflow_id

    def calc_proc_cost(self):
        """ Calculate per-packet processing cost """
        return sum(mod.cost for mod in self.modules)

    def calc_delay_1(self):
        """ Calculate delay according to the new estimate"""
        theta = self.task.calc_theta()
        worker_speed = self.task.worker.speed
        switch = self.task.worker.switch
        queue_size = switch.queue_size
        batch_size = switch.batch_size
        delay_term0 = 0
        for other_task in self.task.worker.tasks:
            if other_task != self.task:
                delay_term0 = max(delay_term0,
                                  settings.C * batch_size * other_task.calc_theta() / worker_speed)
        delay_term1 = queue_size * theta / worker_speed / self.task.weight
        delay_term2 = settings.C * batch_size * theta / worker_speed
        return max(delay_term0, delay_term1) + delay_term2

    def calc_delay_0(self):
        """ Calculate delay according to the old estimate"""
        theta = self.task.calc_theta()
        worker_speed = self.task.worker.speed
        switch = self.task.worker.switch
        queue_size = switch.queue_size
        batch_size = switch.batch_size
        delay_term1 = queue_size * theta / worker_speed / self.task.weight
        delay_term2 = settings.C * batch_size * theta / worker_speed
        return delay_term1 + delay_term2

    def calc_delay(self):
        """ Calculate delay with method depending on settings.DELAY_ESTIMATE_VERSION"""
        if settings.DELAY_ESTIMATE_VERSION == 0:
            return self.calc_delay_0()
        return self.calc_delay_1()

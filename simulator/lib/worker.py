class Worker:
    """ Worker represents a CPU """

    def __init__(self, worker_id, speed, switch, tasks=None):
        self.worker_id = worker_id
        self.switch = switch
        self.speed = speed
        self.tasks = tasks or []

    def __repr__(self):
        return (f"Worker{self.worker_id} on Switch{self.switch.get_id()}: "
                f"tasks: {self.tasks}")

    def get_id(self):
        """ Get Worker ID """
        return self.worker_id

    def add_task(self, task):
        """ Add a task. Returns the added task """
        self.tasks.append(task)
        task.worker = self
        return task

    def detach_task(self, task):
        """ Detach task from worker. Returns the detached task """
        self.tasks.remove(task)
        task.worker = None
        return task

    def has_task_with_id(self, task_id):
        """ Check if worker runs a task given by its task ID """
        if not self.tasks:
            return False
        return any(e for e in self.tasks if e.get_id() == task_id)

    def normalize_task_weights(self):
        """ Normalize task weights to 1 """
        weight_sum = sum(_task.weight for _task in self.tasks)
        for _task in self.tasks:
            _task.weight /= weight_sum

    def get_free_capacity(self):
        """ Returns the free capacity on the worker """
        return self.speed - sum(_task.calc_worker_usage() for _task in self.tasks)

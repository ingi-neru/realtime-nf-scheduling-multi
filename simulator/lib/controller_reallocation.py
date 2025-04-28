import logging


class TaskMigrationController:
    """Task Migration Controller: reallocates resources by distributing
       tasks among workers
    """

    def __init__(self, switch=None, strategies=None):
        """ Create a new TaskMigrationController

            Parameters:
            switch (Switch/None): switch to control
            strategies (list): list of strategies to execute.
              options are: 'all', 'least_constrained', 'flow_affinity', 'greedy'
        """
        self.period = 0
        self.switch = switch
        self.strategies = strategies or ['all']

    def __repr__(self):
        return f"TaskMigration Controller: working on {self.switch} (period: {self.period})"

    def register_switch(self, switch):
        """ Set switch to control """
        self.switch = switch

    @staticmethod
    def __get_least_delayconstrained_task(tasks):
        """ Helper function to choose task with the most headroom for its delay SLO
            from a list of tasks

            Parameter:
            tasks (list): list of tasks

            Returns:
            task_to_move (Task): the task with the most delay budget

        """
        task_min_budgets = {}
        for _task in tasks:
            task_delay_budgets = [_tf.flow.calc_delay_margin()
                                  for _tf in _task.taskflows]
            if any(delay_budget <= 0 for delay_budget in task_delay_budgets):
                # skip tasks that has no delay budget left
                continue
            # store minimum of delay budgets
            task_min_budgets[_task] = min(task_delay_budgets)

        # select task with the highest delay budget
        task_to_move = max(task_min_budgets,
                           key=task_min_budgets.get,
                           default=None)
        return task_to_move

    @staticmethod
    def __get_best_flowaffinity_task(tasks, target_workers):
        """ Helper function to choose task and worker pair
            to decrease flow crossings across workers

            Parameters:
            tasks (list): list of tasks
            target_workers (list): list of target workers

            Returns:
            (task_to_move, target_worker): task and a fitting worker
            to move the choosen task to decrease flow crossings
        """
        flows = set(_tf.flow
                    for _task in tasks
                    for _tf in _task.taskflows)

        # collect flows already on the target workers
        flows_on_targets = {flow: set(tf.task.worker
                                      for tf in flow.taskflows
                                      if tf.task.worker in target_workers)
                            for flow in flows}

        flows_on_tasks = {flow: set(tf.task
                                    for tf in flow.taskflows
                                    if tf.task in tasks)
                          for flow in flows}

        # collect flows on overloaded tasks that
        # are already processed on underloaded workers
        shared_flows = list(set(flows_on_targets).intersection(flows_on_tasks))

        task_to_move = None
        target_worker = None

        # try candidates
        for shared_flow in shared_flows:
            for task in flows_on_tasks[shared_flow]:
                for worker in flows_on_targets[shared_flow]:
                    # check if task would fit to target worker
                    worker_capacity = worker.get_free_capacity()
                    task_load = task.calc_worker_usage()
                    # if it fits, consider it done
                    if worker_capacity > task_load:
                        task_to_move = task
                        target_worker = worker
                        break

        return task_to_move, target_worker

    @staticmethod
    def __get_most_expensive_task(tasks):
        """ Helper function to choose task with the highest processing
            load from a list of tasks

            Parameter:
            tasks (list): list of tasks

            Returns:
            task_to_move (Task): the 'most expensive' task
        """
        task_to_move = tasks[0]
        for _task in tasks:
            if _task.calc_worker_usage() > task_to_move.calc_worker_usage():
                task_to_move = _task
        return task_to_move

    def find_overused_and_underused_workers(self):
        """ Helper function to find overused and underused workers """
        overused_workers = []
        underused_workers = []
        for _worker in self.switch.workers:
            if all(_task.lambd == 0 for _task in _worker.tasks):
                underused_workers.append(_worker)
            else:
                overused_workers.append(_worker)

        return overused_workers, underused_workers
    
    def migrate_task(self, task_to_move, target_worker):
        if task_to_move and target_worker:
            logging.log(logging.INFO, "Moving task %s to worker Worker%d",
                        task_to_move.name, target_worker.get_id())
            task_to_move.migrate_to_worker(target_worker)
    def move_least_constrained_task(self, candidate_tasks, spare_capacities, underused_workers):
        task_to_move = \
            self.__get_least_delayconstrained_task(candidate_tasks)
        if task_to_move:
            task_load = task_to_move.calc_worker_usage()
            target_worker = next((_worker
                                  for _worker in underused_workers
                                  if spare_capacities[_worker.get_id()] > task_load),
                                 None)
        try:
            logging.log(logging.DEBUG,
                        "'least_constrained' strategy result: "
                        "move %s to worker Worker%d",
                        task_to_move.name, target_worker.get_id())
        except AttributeError:
            logging.log(logging.DEBUG,
                        "'least_constrained' strategy result: no move")

    def move_flow_affinity_task(self, candidate_tasks, spare_capacities, underused_workers):
        task_to_move, target_worker = \
        self.__get_best_flowaffinity_task(candidate_tasks,
                                              underused_workers)
        try:
            logging.log(logging.DEBUG,
                        "'flow_affinity' strategy result: move %s to worker Worker%d",
                        task_to_move.name, target_worker.get_id())
        except AttributeError:
            logging.log(logging.DEBUG,
                        "'flow_affinity' strategy result: no move")
    
    def move_greedy_task(self, candidate_tasks, spare_capacities, underused_workers):
        task_to_move = self.__get_most_expensive_task(candidate_tasks)
        task_load = task_to_move.calc_worker_usage()
        target_worker = next((_worker
                              for _worker in underused_workers
                              if spare_capacities[_worker.get_id()] > task_load),
                             None)
        try:
            logging.log(logging.DEBUG,
                        "'greedy' strategy result: move %s to worker Worker%d",
                        task_to_move.name, target_worker.get_id())
        except AttributeError:
            logging.log(logging.DEBUG,
                        "'greedy' strategy result: no move")

    def control(self):
        """ Control function called by the framework """
        logging.log(logging.INFO, "Executing %s", self)

        # collect overused workers and underused workers
        overused_workers, underused_workers = self.find_overused_and_underused_workers()
        logging.log(logging.DEBUG, "Underused Workers: %s",
                    [f"Worker{w.get_id()}" for w in underused_workers])
        logging.log(logging.DEBUG, "Overused Workers: %s",
                    [f"Worker{w.get_id()}" for w in overused_workers])

        # run strategies if there are overused WORKERs and available underused workers
        if overused_workers and underused_workers:
            candidate_tasks = [_task
                               for _worker in overused_workers
                               for _task in _worker.tasks]
            spare_capacities = {_worker.get_id(): _worker.get_free_capacity()
                                for _worker in underused_workers}

            task_to_move = None
            target_worker = None

            # strategy 1: move tasks with least constraining SLOs
            if any(strat in self.strategies for strat in ('all', 'least_constrained')):
                self.move_least_constrained_task(candidate_tasks, spare_capacities, underused_workers) 
            # strategy 2: check flow affinity:
            if any(strat in self.strategies for strat in ('all', 'flow_affinity')):
                self.move_flow_affinity_task(candidate_tasks, spare_capacities, underused_workers)
            # strategy 3: greedy: move most extensive task
            if any(strat in self.strategies for strat in ('all', 'greedy')):
                self.move_greedy_task(candidate_tasks, spare_capacities, underused_workers)
            # move task
            self.migrate_task(task_to_move, target_worker)
        # increase period counter
        self.period += 1

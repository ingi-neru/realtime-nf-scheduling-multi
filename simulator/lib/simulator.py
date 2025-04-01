import csv
import logging
import sys

import numpy as np
from scipy.optimize import linprog

from . import controller_endtoend
from . import controller_reallocation
from . import controller_switch
from . import flow
from . import module
from . import switch
from . import task
from . import taskflow
from . import utils
from . import worker

# config numpy to fully print matrix A
np.set_printoptions(threshold=sys.maxsize)


class Simulator:
    """ RT Switch Simulator main class"""

    def __init__(self, name='', simulator_params=None):
        self.name = name
        self.simulator_params = simulator_params
        self.switches = []
        self.results = []
        self.endtoend_controller = None

    def init_from_gml(self, nx_graph, weights):
        """ Read configuration from GML file """

        # read graph parameters
        self.name = nx_graph.graph['name']

        switch_ids = {attr.get('switch', 0): None
                      for _, attr in nx_graph.nodes(data=True)}

        use_endtoend_controller = bool(nx_graph.graph.get('endtoend_controller', 0))


        # init modules
        modules = [module.Module(cost=attr['cost'], module_id=node)
                   for node, attr in nx_graph.nodes(data=True)]

        # init flows
        flows_dict = {}
        for node_id, attr in nx_graph.nodes(data=True):
            _module = modules[node_id-1]
            # flow attributes are stored in a list..
            if isinstance(attr['flows']['flow'], list):
                for _flow in attr['flows']['flow']:
                    if not _flow['flowid'] in flows_dict:
                        flows_dict[_flow['flowid']] = _flow
                        flows_dict[_flow['flowid']]['path'] = []
                    flows_dict[_flow['flowid']]['path'].append(_module)
            # ..or in a dict; this is networkx-specific
            elif isinstance(attr['flows']['flow'], dict):
                _flow = dict(f for f in attr['flows']['flow'].items())
                if not _flow['flowid'] in flows_dict:
                    flows_dict[_flow['flowid']] = _flow
                    flows_dict[_flow['flowid']]['path'] = []
                flows_dict[_flow['flowid']]['path'].append(_module)
            else:
                raise ValueError("Invalid flow data!")
        print(flows_dict)
        flows = [flow.Flow(taskflows=[],
                           slo_params={'delay': f['flowdelaySLO'],
                                       'rate': f['flowrateSLO']},
        rate=f['flowrate'],
                           name=f['flowname'],
                           flow_id=f['flowid'])
                 for _, f in flows_dict.items()]
        flow_paths = {k: f['path'] for k, f in flows_dict.items()}

        # init switches
        for switch_id in switch_ids:
            realloc_bool = bool(nx_graph.graph.get('resource_reallocation', 0))
            realloc_strat = nx_graph.graph.get('reallocation_strategies', 'all')
            switch_params = {
                'queue_size': nx_graph.graph['Q'],
                'batch_size': nx_graph.graph['B'],
                'resource_reallocation': realloc_bool,
                'reallocation_strategy': realloc_strat,
                'switch_id': switch_id,
            }

            # init workers
            worker_speeds = {attr['worker']: attr['workerspeed']
                             for _, attr in nx_graph.nodes(data=True)
                             if attr.get('switch', 0) == switch_id}


            workers = [worker.Worker(wid, speed, switch=None, tasks=None)
                       for wid, speed in worker_speeds.items()]

            while len(workers) < nx_graph.graph.get('num_workers', 0):
                workers.append(
                    worker.Worker(len(workers),
                                  workers[0].speed,
                                  switch=None,
                                  tasks=None)
                )
            
            # init tasks
            task_counter = 0
            for _, attr in nx_graph.nodes(data=True):
                wid = attr['worker']
                if attr.get('switch', 0) == switch_id and \
                   not workers[wid].has_task_with_id(attr['task']):
                    # add task to worker
                    workers[wid].add_task(
                        task.Task(
                            name=attr['taskname'],
                            worker=workers[wid],
                            weight=weights[task_counter],
                            task_id=attr['task'],
                            switch_id=switch_id
                        )
                    )
                    task_counter += 1

            # create taskflows
            for _flow in flows:
                flow_modules = flow_paths[_flow.get_id()]
                for flow_module in flow_modules:
                    node = nx_graph.nodes()[flow_module.get_id()]
                    _worker = next((w for w in workers
                                    if w.get_id() == node['worker']
                                    and node.get('switch', 0) == switch_id),
                                   None)
                    if _worker is None:
                        # worker runs on different switch, we will
                        # handle that later
                        continue
                    _task = next(t for t in _worker.tasks
                                 if t.get_id() == node['task'])
                    if not _task.has_taskflow_with_id(_flow.get_id()):
                        tflow = taskflow.TaskFlow(
                            modules=[flow_module],
                            taskflow_id=_flow.get_id(),
                            task=_task,
                            flow=_flow)
                        _task.add_taskflow(tflow)
                        _flow.add_taskflow(tflow)
                    else:
                        tflow = _task.get_taskflow_by_id(_flow.get_id())
                        if tflow:
                            tflow.modules.append(flow_module)

            # create controllers and switch
            controller = controller_switch.SwitchController(None)
            realloc_controller = None
            if switch_params['resource_reallocation']:
                realloc_controller = \
                    controller_reallocation.TaskMigrationController(switch=None,
                                                                    strategies=realloc_strat)
            print("registering new switch with id: ", switch_id)
            new_switch = switch.Switch(
                simulator=self,
                controller=controller,
                reallocation_controller=realloc_controller,
                flows=flows,
                workers=workers,
                switch_params=switch_params,
                switch_id=switch_id
            )
            # add switch controller
            controller.register_switch(new_switch)
            if realloc_controller:
                realloc_controller.register_switch(new_switch)
            # assign workers to the switch
            for _worker in workers:
                _worker.switch = new_switch

            print(workers)
            self.switches.append(new_switch)

        if use_endtoend_controller:
            new_ctrlr = controller_endtoend.EndToEndController(self.switches)
            self.endtoend_controller = new_ctrlr

        print(self.switches)

    def __simulate_switch(self, switch_obj):
        """ Run a switch simulator for a single period

           Parameters:
           switch_obj (Switch): switch to simulate
        """
        tasks = [_task
                 for _worker in switch_obj.workers
                 for _task in _worker.tasks]
        num_flows = len(switch_obj.flows)
        num_taskflows = sum(1
                            for _task in tasks
                            for _ in _task.taskflows)
        

        num_tasks = len(tasks)
        num_task_crossings = sum(1    
                                 for _flow in switch_obj.flows
                                 for _taskflow in _flow.taskflows
                                 if _taskflow.task.switch_id == switch_obj.switch_id
                                 )
        
        cross_switch_tasks, cross_task_values = [], []
        num_columns = num_taskflows + num_flows
        num_rows = num_tasks + num_flows + len(cross_switch_tasks) + num_task_crossings
        print("num_rows = ", num_rows, " = ", num_tasks, " + ", num_flows, " + ", len(cross_switch_tasks), " + ", num_task_crossings)
        print("num_columns: ", num_columns, " = ", num_taskflows, " + ", num_flows)
        print(cross_switch_tasks)


        # Note: scipy MINIMIZEs the obj function, thus, to maximize
        # the sum of the x-es, we do c *= -1
        coeffs = [0] * num_taskflows + [-1] * num_flows
        # set variable bounds
        upper_bounds = ([_tflow.flow.rate
                         for _task in tasks
                         for _tflow in _task.taskflows] +
                        [_flow.rate for _flow in switch_obj.flows])
        bounds = np.zeros((num_columns, 2))
        for i in range(num_columns):
            # set lower bounds
            bounds[i][0] = 0
            # set upper bounds
            bounds[i][1] = upper_bounds[i]

        # construct A matrix
        A = np.zeros((num_rows, num_columns))
        counter = 0
        for i in range(num_tasks):
            for _tflow in tasks[i].taskflows:
                A[i][counter] = _tflow.calc_proc_cost()
                counter += 1

        row_idx = num_tasks
        for idx, _flow in enumerate(switch_obj.flows):
            task_crossings = [(arc[0].task, arc[1].task)
                              for arc in utils.pairwise(_flow.taskflows)]
            for src_task, dst_task in task_crossings:
                if src_task not in tasks or dst_task not in tasks:
                    continue
                src_idx = sum(len(_task.taskflows)
                              for _task in tasks[:tasks.index(src_task)])
                dst_idx = sum(len(_task.taskflows)
                              for _task in tasks[:tasks.index(dst_task)])
                A[row_idx][min(src_idx + idx, num_taskflows - 1)] = 1
                A[row_idx][min(dst_idx + idx, num_taskflows - 1)] = -1
                row_idx += 1
            _tmp_idx = num_tasks + num_task_crossings + idx
            if _flow.taskflows[0].task not in tasks:
                A[_tmp_idx][idx] = -1
            else:
                A[_tmp_idx][tasks.index(_flow.taskflows[0].task) + idx] = -1
            A[_tmp_idx][num_taskflows + idx] = 1

        # construct B vector
        b = np.zeros(num_rows)
        for i, _task in enumerate(tasks):
            b[i] = _task.weight * _task.worker.speed
        for i, _task in enumerate(cross_switch_tasks):
            _tmp_idx = num_tasks + num_flows + num_task_crossings + i
            # Example constraint: Ensure cross-switch task doesn't exceed local flow rate
            task_idx = sum(len(_task.taskflows)
                            for _task in cross_switch_tasks[:cross_switch_tasks.index(_task)])
            A[_tmp_idx][min(task_idx + i, len(cross_switch_tasks) - 1)] = -1  # Adjust idx based on flow index
            b[_tmp_idx] = 0
        A_upperbound = A[:num_tasks, ]
        A_equality = A[num_tasks:, ]

        b_upperbound = b[:num_tasks]
        b_equality = b[num_tasks:]

        # solve the linear program
        res = linprog(c=coeffs,
                      A_ub=A_upperbound,
                      b_ub=b_upperbound,
                      A_eq=A_equality,
                      b_eq=b_equality,
                      bounds=(bounds),
                      #method='revised simplex',
                      )

        logging.log(logging.DEBUG, "bounds:\n%s", bounds)
        logging.log(logging.DEBUG, "'c':\n%s", coeffs)
        logging.log(logging.DEBUG, "'b' vector:\n%s", b)
        logging.log(logging.DEBUG, "'A' matrix:\n%s", A)
        logging.log(logging.DEBUG, "Linear Program Results:\n%s", res)


        # update flow rates
        for idx, _flow in enumerate(switch_obj.flows):
            _flow.current_rate = res.x[num_taskflows + idx]


        # update task lambdas
        delta = self.simulator_params['delta']
        for t_idx, _task in enumerate(tasks):
            logging.log(logging.DEBUG, "\ntask id `_task.get_id()' %s", _task.get_id())
            _task.lambd = 0
            demand_for_more_traffic = False
            for tf_idx, _tflow in enumerate(_task.taskflows):
                logging.log(logging.DEBUG, "taskflow id `tf_idx' %s", tf_idx)
                rate_limit = (1 - delta) * res.x[num_taskflows + tf_idx]
                logging.log(logging.DEBUG, "at taskflow, `rate_limit' %s", rate_limit)
                logging.log(logging.DEBUG, "`_tflow.flow.slo_params['rate']' %s", _tflow.flow.slo_params['rate'])
                logging.log(logging.DEBUG, "`_tflow.flow.current_rate' %s", _tflow.flow.rate)
                logging.log(logging.DEBUG, "`min(_tflow.flow.slo_params['rate'], _tflow.flow.rate)' %s", min(_tflow.flow.slo_params['rate'], _tflow.flow.rate))
                if  rate_limit <= min(_tflow.flow.slo_params['rate'], _tflow.flow.rate):
                    demand_for_more_traffic = True
                    logging.log(logging.DEBUG, "Needed more rate/weight at task %s", _task.get_id())
                    break
            if demand_for_more_traffic:
                _tresh = (1 - delta) * b[t_idx]
                if np.dot(A[t_idx], res.x) >= _tresh:
                    _task.lambd = 1



    def __simulate_switches(self):
        """ Simulate switches one after the other """
        for _switch in self.switches:
            self.__simulate_switch(_switch)

    def __collect_simulation_results(self):
        """ Collect simulation results """
        result = {}
        for _switch in self.switches:
            # flow results
            for _flow in _switch.flows:
                result[f'rate[{_flow.name}]'] = _flow.current_rate
                result[f'rate_slo[{_flow.name}]'] = _flow.slo_params['rate']
                result[f'delay[{_flow.name}]'] = _flow.calc_delay()
                result[f'delay_slo[{_flow.name}]'] = _flow.slo_params['delay']
            # task results
            for _worker in _switch.workers:
                for _task in _worker.tasks:
                    result[f'weight[{_task.name}]'] = _task.weight
                    result[f'lambda[{_task.name}]'] = _task.lambd
        return result

    def __run_one_simulation_round(self, sim_round=0, warmup=False):
        """ Run a single simulation round.

            Parameter:
            warmup (bool): if enabled, controller action is skipped
        """

        # run controllers
        if not warmup:

            # resource reallocation
            if sim_round % self.simulator_params['realloc_interval'] == 0:
                for _switch in self.switches:
                    if _switch.reallocation_controller:
                        _switch.reallocation_controller.control()

            # end to end controller or switch controllers
            if self.endtoend_controller:
                self.endtoend_controller.control()
            else:
                for _switch in self.switches:
                    _switch.controller.control()

        # run simulator (new flow rates and lambdas, etc.)
        self.__simulate_switches()

        # collect data
        self.results.append(self.__collect_simulation_results())

    def run_simulation(self, rounds):
        """ Run the simulation over the given rounds """
        logging.log(logging.INFO, "* Running Simulation on '%s'", self.name)
        # run a warmup round and collect initial state
        self.__run_one_simulation_round(sim_round=0, warmup=True)
        # run simulation rounds
        for count in range(1, rounds+1):
            logging.log(logging.INFO, "** Simulation Round %d", count)
            self.__run_one_simulation_round(sim_round=count, warmup=False)

    def write_results(self, out_file):
        """ Write simulation results to CSV file """
        with open(out_file, 'w') as outfile:
            csv_writer = csv.DictWriter(outfile,
                                        fieldnames=self.results[0].keys())
            csv_writer.writeheader()
            csv_writer.writerows(self.results)

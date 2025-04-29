import logging

import numpy as np

from . import settings
from . import switch
from .controller_common_fns import ControllerCommonFns as common_functions

class SwitchController:
    """ Controller for a Switch """

    def __init__(self, switch=switch):
        self.period = 0
        self.switch = switch

    def __repr__(self):
        return f"SwitchController: working on {self.switch} (period: {self.period})"

    def register_switch(self, switch):
        """ Set switch to control """
        self.switch = switch

    def w_corner_points_for_control_2(self, w_start, d, _worker, rho_roughness):
        w_corner_points = []
        w_corner_points.append(w_start)

        w_local_original = [_task.weight for _task in _worker.tasks]
        w_local = w_local_original

        tasks_blocked = [False] * len(_worker.tasks)
        while False in tasks_blocked:
            logging.log(logging.DEBUG,
                        "Tasks blocked:\n %s", tasks_blocked)

            d_len = len(d)
            eye_mx = np.eye(d_len)
            one_over_n_matrix = np.ones((d_len, d_len),
                                        dtype=float) / int(d_len)
            d = np.dot(eye_mx - one_over_n_matrix, d)
            if np.linalg.norm(d) < settings.DEFAULT_EPSILON:
                logging.log(logging.DEBUG,
                            "Norm of projected d vector is very small. Stopping.")
                break
            decreaser = settings.M
            increaser = settings.M
            proportion_decreaser = settings.M
            proportion_decreaser_id = -1
            not_weightless = settings.M
            counter = 0
            for i in range(len(w_local)):
                if not tasks_blocked[i]:
                    task_weight = w_local[i]
                    logging.log(logging.DEBUG,
                                "Task_counter_ %s", tasks_blocked)

                    if d[counter] < 0 and task_weight / -d[counter] < decreaser:
                        decreaser = task_weight / -d[counter]
                    if d[counter] > 0 and (1 - task_weight) / d[counter] < increaser:
                        increaser = (1 - task_weight) / d[counter]
                    if d[counter] < 0 and abs(task_weight / d[counter] / 2) < proportion_decreaser:
                        proportion_decreaser = abs(
                            task_weight / d[counter] / 2)
                        proportion_decreaser_id = i
                    if d[counter] < 0 and task_weight + d[counter] < 2 * settings.DEFAULT_EPSILON:
                        not_weightless = (
                            settings.DEFAULT_EPSILON / 2 - task_weight) / d[counter]
                    counter += 1
            nue = min(decreaser,
                      increaser,
                      proportion_decreaser,
                      not_weightless)

            proportion_blocker = nue

            # pylint: disable=W1202
            logging.log(logging.DEBUG,
                        "Line search internal variables:\n%s",
                        '\n'.join((f"decreaser: {decreaser}",
                                   f"increaser: {increaser}",
                                   f"proportion_decreaser: {proportion_decreaser}",
                                   f"not_weightless: {not_weightless}",
                                   f"nue: {nue}",
                                   f"d*nue: {d*nue}",
                                   ))
                        )

            logging.log(logging.INFO, "Line search task updates:")
            counter = 0
            new_d = []
            for i in range(len(_worker.tasks)):
                if not tasks_blocked[i]:
                    w_local[i] += nue * d[counter]
                    logging.log(logging.INFO,
                                "Task%d was not blocked; its new weight is: %f",
                                i, w_local[i])
                    if w_local[i] >= 1 - 2 * settings.DEFAULT_EPSILON or \
                            w_local[i] < 2 * settings.DEFAULT_EPSILON or \
                            (proportion_blocker and proportion_decreaser_id == i):
                        tasks_blocked[i] = True
                        logging.log(logging.DEBUG,
                                    "Task%d was removed from line search", i)
                    if not tasks_blocked[i]:
                        new_d.append(d[counter])
                    counter += 1
            if all(x > 0 for x in w_local):
                w_corner_points.append(w_local)
            else:
                logging.log(
                    logging.INFO, "Something went wrong: negative weight encountered.")
                return np.asarray([0, 0])
            d = new_d
            logging.log(logging.DEBUG,
                        "'new_d' vector before projection:\n %s", d)

        # pruning so that no weight could change more than rho_roughness
        w_corner_points = np.asarray(w_corner_points)
        logging.log(logging.DEBUG,
                    "'w_corner_points' vector:\n %s", w_corner_points)
        nue = rho_roughness
        w_corner_points_final = [w_corner_points[0]]
        i = 1
        logging.log(logging.DEBUG, 'WE WILL START THE WHILE. SEEMS FINE')
        logging.log(logging.DEBUG, 'nue: ' + str(nue))
        while nue > 0 and i < len(w_corner_points):
            logging.log(logging.DEBUG, 'JUST ANOTHER WHILE CIRCLE. SEEMS FINE')
            segment_size = np.linalg.norm(
                w_corner_points[i] - w_corner_points[i-1])
            if segment_size < nue:
                logging.log(logging.DEBUG,
                            'JUST ANOTHER CORNER POINT. SEEMS FINE')
                w_corner_points_final.append(w_corner_points[i])
            else:
                logging.log(logging.DEBUG, 'EXCEEDING RHO. SEEMS FINE')
                w_corner_points_final.append(
                    w_corner_points[i-1] + (w_corner_points[i] -
                                            w_corner_points[i-1]) * nue / segment_size
                )
            nue -= segment_size
            i += 1

        logging.log(
            logging.DEBUG, "'w_corner_points_final' vector:\n %s", w_corner_points_final)
        return np.asarray(w_corner_points_final)
    

    def obj_val_end_to_end(self, _worker, weights):
        print("Used end to end fn eval.")
        flows = []
        for _switch in self.switch.simulator.switches:
            for _flow in _switch.flows:
                if _flow not in flows:
                    flows.append(_flow)

        sum_excess_flow_delays = 0
        for _flow in self.switch.flows:
            flow_delay = common_functions.calc_flow_delay(_worker, _flow, weights)
            sum_excess_flow_delays += (flow_delay / _flow.slo_params['delay'])
            logging.log(
                logging.DEBUG, "'delay and dSLO of flow named': %s", _flow.flow_id)
            logging.log(logging.DEBUG, " %s",  flow_delay)
            logging.log(logging.DEBUG, "%s", _flow.slo_params['delay'])
        logging.log(logging.DEBUG, "'sum_excess_flow_delays': %s",
                    sum_excess_flow_delays)

        sum_weighted_lambdas = 0
        j = 0
        for _task in _worker.tasks:
            sum_weighted_lambdas += _task.lambd * weights[j]
            j += 1
        for _other_worker in self.switch.workers:
            if _other_worker != _worker:
                for _task in _other_worker.tasks:
                    sum_weighted_lambdas += _task.lambd * _task.weight
        logging.log(logging.DEBUG, "'sum_weighted_lambdas': %s",
                    sum_weighted_lambdas)

        alpha = self.switch.simulator.simulator_params['alpha']
        obj_val = alpha * sum_excess_flow_delays - sum_weighted_lambdas
        logging.log(
            logging.DEBUG, "'obj_val (alpha * exc.delays - wghtd.ls)': %s", obj_val)
        return obj_val

    def obj_val(self, _worker, weights):
        sum_excess_flow_delays = 0
        for _flow in self.switch.flows:
            flow_delay = common_functions.calc_flow_delay(_worker, _flow, weights)
            sum_excess_flow_delays += max(0,
                                          flow_delay - _flow.slo_params['delay'])
            logging.log(
                logging.DEBUG, "'delay and dSLO of flow named': %s", _flow.flow_id)
            logging.log(logging.DEBUG, " %s",  flow_delay)
            logging.log(logging.DEBUG, "%s", _flow.slo_params['delay'])
            # logging.log(logging.DEBUG, "'delay SLO of flow': %s", _flow.flow_id, _flow.slo_params['delay'])
        logging.log(logging.DEBUG, "'sum_excess_flow_delays': %s",
                    sum_excess_flow_delays)

        sum_weighted_lambdas = 0
        j = 0
        for _task in _worker.tasks:
            sum_weighted_lambdas += _task.lambd * weights[j]
            j += 1
        for _other_worker in self.switch.workers:
            if _other_worker != _worker:
                for _task in _other_worker.tasks:
                    sum_weighted_lambdas += _task.lambd * _task.weight
        logging.log(logging.DEBUG, "'sum_weighted_lambdas': %s",
                    sum_weighted_lambdas)

        alpha = self.switch.simulator.simulator_params['alpha']
        obj_val = alpha * sum_excess_flow_delays - sum_weighted_lambdas
        logging.log(
            logging.DEBUG, "'obj_val (alpha * exc.delays - wghtd.ls)': %s", obj_val)
        return obj_val

    def arg_opt_obj_val_on_line_segment(self, _worker, a, b):
        obj_val = self.obj_val
        if self.switch.simulator.endtoend_controller:
            obj_val = self.obj_val_end_to_end
        v = b - a
        quantum = [x / settings.LINEAR_SEARCH_TRIES for x in v]
        w_try = a.copy()
        # objective value of the starting point:
        best_obj_val = obj_val(_worker, w_try)
        best_w = a.copy()
        for _ in range(settings.LINEAR_SEARCH_TRIES):
            # w_try = a.copy() + [x * j for x in quantum]
            w_try += list(quantum)
            logging.log(logging.DEBUG, "Weight tried out: %s", w_try)
            curr_obj_val = obj_val(_worker, w_try)
            logging.log(logging.DEBUG,
                        "Its objective value: %s", curr_obj_val)
            if curr_obj_val < best_obj_val:
                best_obj_val = curr_obj_val
                best_w = w_try.copy()
        logging.log(logging.DEBUG,
                    "Argument of best objective value above (best_w): %s", best_w)
        return best_w

    def arg_opt_obj_val_on_polyline(self, _worker, cornerpoints):
        best_obj_val = settings.M
        best_w = cornerpoints[0].copy()
        for i in range(len(cornerpoints)-1):
            inner_best_w = self.arg_opt_obj_val_on_line_segment(
                _worker, cornerpoints[i], cornerpoints[i+1])
            inner_best_obj_val = self.obj_val(_worker, inner_best_w)
            if inner_best_obj_val < best_obj_val:
                best_obj_val = inner_best_obj_val
                best_w = inner_best_w

        while True:
            if not np.array_equal(best_w, cornerpoints[0]):
                break
            else:
                logging.log(
                    logging.DEBUG, "New weights will be very close to the former w. Searching around it\n %s", self)
                best_w = self.arg_opt_obj_val_on_line_segment(
                    _worker, cornerpoints[0], cornerpoints[1])
                v = cornerpoints[1] - cornerpoints[0]
                quantum = [x / settings.LINEAR_SEARCH_TRIES for x in v]
                cornerpoints[1] = cornerpoints[0] + quantum
        return best_w
 
    def control_2(self):
        """ Control function called by the framework. """
        logging.log(logging.INFO, "Executing %s", self)

        # control algorithm: a sort of line search
        for _worker in self.switch.workers:

            logging.log(logging.INFO, "Objective Value at Worker at the start of control period: %s",
                        self.obj_val(_worker, [_task.weight for _task in _worker.tasks]))

            num_worker_tasks = len(_worker.tasks)
            # skip if worker runs 0 or 1 tasks
            if num_worker_tasks < 2:
                continue

            # calculating d:
            d = np.array([_task.calc_load_deriv()
                          for _task in _worker.tasks])
            logging.log(logging.DEBUG, "'d' vector:\n %s", d)

            d_len = len(d)
            eye_mx = np.eye(d_len)
            one_over_n_matrix = np.ones((d_len, d_len),
                                        dtype=float) / int(d_len)
            P = eye_mx - one_over_n_matrix
            d = np.dot(P, d)

            if np.linalg.norm(d, np.inf) > 0.1: # Why do we need this?
                d = [x * 0.1 / np.linalg.norm(d, np.inf)
                     for x in d]

            logging.log(logging.DEBUG,
                        "projected and scaled 'd' vector:\n %s", d)
            if np.linalg.norm(d, np.inf) > 0:
                w_local = [_task.weight for _task in _worker.tasks]
                logging.log(logging.DEBUG,
                            "'w_local' vector:\n %s", w_local)

                corner_points = self.w_corner_points_for_control_2(w_local, d, _worker,
                                                                   self.switch.simulator.simulator_params['rho_roughness'])
                w_got = self.arg_opt_obj_val_on_line_segment(
                    _worker, corner_points[0], corner_points[1])
                j = 0
                for _task in _worker.tasks:
                    _task.weight = w_got[j]
                    j += 1


        # calculate obj function value for DEBUG purposes
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            obj_func_value = {f"Worker{_worker.get_id()}":
                              min(settings.M,
                                  min((_task.calc_load()
                                       for _task in _worker.tasks),
                                      default=settings.M))
                              for _worker in self.switch.workers}
            logging.log(logging.DEBUG,
                        "'L' Obj function value:\n %s", obj_func_value)

        # norm weights on workers
        logging.log(logging.INFO,
                    "Updated and scaled weights on Workers")
        for _worker in self.switch.workers:
            _worker.normalize_task_weights()
            logging.log(logging.INFO, "Worker%d: %s",
                        _worker.get_id(), {t.task_id: t.weight for t in _worker.tasks})

        # increase period counter
        self.period += 1

    def control_1(self):
        """ Control function called by the framework. """
        logging.log(logging.INFO, "Executing %s", self)
        eps = self.switch.simulator.simulator_params['eps']
        rho_roughness = self.switch.simulator.simulator_params['rho_roughness']

        # control algorithm: a sort of line search
        for _worker in self.switch.workers:
            num_worker_tasks = len(_worker.tasks)
            # skip if worker runs 0 or 1 tasks
            if num_worker_tasks < 2:
                continue
            tasks_blocked = [False] * num_worker_tasks
            logging.log(logging.DEBUG,
                        "Tasks blocked:\n %s", tasks_blocked)

            # calculating d:
            d = np.array([_task.calc_load_deriv()
                          for _task in _worker.tasks])
            logging.log(logging.DEBUG, "'d' vector:\n %s", d)

            d_len = len(d)
            eye_mx = np.eye(d_len)
            one_over_n_matrix = np.ones((d_len, d_len),
                                        dtype=float) / int(d_len)
            P = eye_mx - one_over_n_matrix
            d = np.dot(P, d)

            if np.linalg.norm(d, np.inf) > 0.1:
                d = [x / (np.linalg.norm(d, np.inf) * 0.1)
                     for x in d]

            logging.log(logging.DEBUG,
                        "projected and scaled 'd' vector:\n %s", d)

            d_further_scaled_num = 0
            # if np.linalg.norm(d, np.inf)> eps/100000000:
            if np.linalg.norm(d, np.inf) > 0:
                A = - np.eye(d_len)
                w_local = [_task.weight for _task in _worker.tasks]

                logging.log(logging.DEBUG,
                            "'w_local' vector:\n %s", w_local)

                b_hat = - np.dot(A, w_local.copy())  # b = 0
                d_hat = np.dot(A, d)
                nue_max = settings.M
                for i in range(d_len):
                    if d_hat[i] > 0 and (b_hat[i]/d_hat[i] < nue_max):
                        nue_max = b_hat[i]/d_hat[i]

                quantum = nue_max / settings.LINEAR_SEARCH_TRIES
                logging.log(logging.DEBUG, "'quantum' :\n %s", quantum)

                final_best_i = - 1
                while True:
                    best_i = -1
                    best_obj_val = settings.M

                    for i in range(settings.LINEAR_SEARCH_TRIES):
                        #w_try = w_local +  i * quantum * d
                        w_try = w_local.copy()
                        logging.log(logging.DEBUG,
                                    "'w_local' vector:\n %s", w_local)
                        logging.log(
                            logging.DEBUG, "'w_local as w_try entry' vector:\n %s", w_try)
                        tobreak = False
                        for j in range(len(w_try)):
                            w_try[j] += i * quantum * d[j]
                            if w_try[j] <= 0:
                                tobreak = True
                        logging.log(logging.DEBUG,
                                    "'w_try' vector:\n %s", w_try)
                        if tobreak:
                            break

                        j = 0
                        for _task in _worker.tasks:
                            _task.weight = w_try[j]
                            j += 1

                        sum_excess_flow_delays = 0
                        for _flow in self.switch.flows:
                            flow_delay = 0
                            j = 0
                            for _task in _worker.tasks:
                                flow_delay += _task.calc_time_if_full_weight() / \
                                    w_try[j]
                                j += 1
                            for _taskflow in _flow.taskflows:
                                if _taskflow.task not in _worker.tasks:
                                    flow_delay += _taskflow.task.calc_time_if_full_weight() / \
                                        w_try[j]
                            sum_excess_flow_delays += max(
                                0, flow_delay - _flow.slo_params['delay'])

                        sum_weighted_lambdas = 0
                        j = 0
                        for _task in _worker.tasks:
                            sum_weighted_lambdas += _task.lambd * w_try[j]
                            j += 1
                        for _other_worker in self.switch.workers:
                            if _other_worker != _worker:
                                for _task in _other_worker.tasks:
                                    sum_weighted_lambdas += _task.lambd * _task.weight

                        alpha = self.switch.simulator.simulator_params['alpha']
                        obj_val = alpha * sum_excess_flow_delays - sum_weighted_lambdas

                        if obj_val < best_obj_val:
                            best_obj_val = obj_val
                            best_i = i
                    if best_i < 1:
                        if best_i == -1:
                            raise ValueError(
                                'A very specific bad thing happened: we did not give value to variable best_i')
                        d = [x / settings.LINEAR_SEARCH_TRIES for x in d]
                        d_further_scaled_num += 1
                        logging.log(logging.DEBUG, "'d' vector:\n %s", d)
                        logging.log(
                            logging.DEBUG, "'d' further down scaled number:\n %s", d_further_scaled_num)
                    else:
                        final_best_i = best_i
                        break

                w_got = w_local.copy()
                for j in range(len(w_got)):
                    w_got[j] += final_best_i * quantum * d[j]
                logging.log(logging.DEBUG, "'best_i' :\n %s", best_i)
                logging.log(logging.DEBUG, "'quantum' :\n %s", quantum)
                logging.log(logging.DEBUG,
                            "'w_local' vector:\n %s", w_local)
                logging.log(logging.DEBUG, "'d' vector:\n %s", d)
                logging.log(logging.DEBUG, "'w_got' vector:\n %s", w_got)

                j = 0
                for _task in _worker.tasks:
                    _task.weight = w_got[j]
                    j += 1

        # calculate obj function value for DEBUG purposes
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            obj_func_value = {f"Worker{_worker.get_id()}":
                              min(settings.M,
                                  min(_task.calc_load()
                                      for _task in _worker.tasks))
                              for _worker in self.switch.workers}
            logging.log(logging.DEBUG,
                        "'L' Obj function value:\n %s", obj_func_value)

        # increase period counter
        self.period += 1

    def control_0(self):
        """ Control function called by the framework. """
        logging.log(logging.INFO, "Executing %s", self)
        eps = self.switch.simulator.simulator_params['eps']
        rho_roughness = self.switch.simulator.simulator_params['rho_roughness']

        # control algorithm: a sort of line search
        for _worker in self.switch.workers:

            logging.log(logging.INFO, "Objective Value at Worker at the start of control period: %s",
                        self.obj_val(_worker, [_task.weight for _task in _worker.tasks]))

            num_worker_tasks = len(_worker.tasks)
            # skip if worker runs 0 or 1 tasks
            if num_worker_tasks < 2:
                continue
            tasks_blocked = [False] * num_worker_tasks
            logging.log(logging.DEBUG,
                        "Tasks blocked:\n %s", tasks_blocked)

            # calculating d:
            load_deriv = np.array([_task.calc_load_deriv()
                                   for _task in _worker.tasks])
            logging.log(logging.DEBUG,
                        "Load derivatives:\n %s", load_deriv)

            mue = rho_roughness
            if np.linalg.norm(load_deriv, np.inf) > mue:
                d = [x * mue / np.linalg.norm(load_deriv, np.inf)
                     for x in load_deriv]
            else:
                d = load_deriv
            logging.log(logging.DEBUG, "'d' vector:\n %s", d)

            # way traversed so far out of the step size mue=rho_roughness
            delta = 0
            while (False in tasks_blocked and (delta <= mue - eps)):
                d_len = len(d)
                eye_mx = np.eye(d_len)
                one_over_n_matrix = np.ones((d_len, d_len),
                                            dtype=float) / int(d_len)
                d = np.dot(eye_mx - one_over_n_matrix, d)
                if np.linalg.norm(d) < eps:
                    break
                decreaser = settings.M
                increaser = settings.M
                proportion_decreaser = settings.M
                proportion_decreaser_id = -1
                not_weightless = settings.M
                for i in range(d_len):
                    if not tasks_blocked[i]:
                        task_weight = _worker.tasks[i].weight
                        if d[i] < 0 and task_weight / -d[i] < decreaser:
                            decreaser = task_weight / -d[i]
                        if d[i] > 0 and (1 - task_weight) / d[i] < increaser:
                            increaser = (1 - task_weight) / d[i]
                        if d[i] < 0 and abs(task_weight / d[i] / 2) < proportion_decreaser:
                            proportion_decreaser = abs(task_weight / d[i] / 2)
                            proportion_decreaser_id = i
                        if d[i] < 0 and task_weight+d[i] < 2 * eps:
                            not_weightless = (eps / 2 - task_weight) / d[i]
                nue = min(mue - delta,
                          min(decreaser,
                              increaser,
                              proportion_decreaser,
                              not_weightless)
                          )

                proportion_blocker = nue == proportion_decreaser

                # pylint: disable=W1202
                logging.log(logging.DEBUG,
                            "Line search internal variables:\n%s",
                            '\n'.join((f"decreaser: {decreaser}",
                                       f"increaser: {increaser}",
                                       f"proportion_decreaser: {proportion_decreaser}",
                                       f"not_weightless: {not_weightless}",
                                       f"mue: {mue}",
                                       f"delta: {delta}",
                                       f"nue: {nue}"))
                            )

                logging.log(logging.INFO, "Line search task updates:")
                counter = 0
                new_d = []
                for i in range(num_worker_tasks):
                    if not tasks_blocked[i]:
                        _worker.tasks[i].weight += nue * d[counter]
                        logging.log(logging.INFO,
                                    "Task%d was not blocked; its new weight is: %f",
                                    i, _worker.tasks[i].weight)
                        if _worker.tasks[i].weight >= 1 - 2 * eps or \
                                _worker.tasks[i].weight < 2 * eps or \
                           (proportion_blocker and proportion_decreaser_id == i):
                            tasks_blocked[i] = True
                            logging.log(logging.DEBUG,
                                        "Task%d was removed from line search", i)
                        if not tasks_blocked[i]:
                            new_d.append(d[counter])
                        counter += 1
                delta += nue
                d = new_d

        # norm weights on workers
        logging.log(logging.INFO,
                    "Updated and scaled weight for workers")
        for _worker in self.switch.workers:
            _worker.normalize_task_weights()
            logging.log(logging.INFO, "Worker%d: %s",
                        _worker.get_id(), {t.task_id: t.weight for t in _worker.tasks})

        # increase period counter
        self.period += 1

    def control(self):
        if settings.CONTROL_VERSION == 0:
            return self.control_0()
        if settings.CONTROL_VERSION == 1:
            return self.control_1()
        return self.control_2()

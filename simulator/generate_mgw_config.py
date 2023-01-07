#!/usr/bin/env python3
"""Helper script to generate MGW (mobile gateway) config as a GML
(Graph Modelling Language) file.

Based on
https://github.com/levaitamas/dataflow_graph_embedding/blob/master/utils/gen_mgw_lgf.py

"""
import argparse
import random


# Settings

FLOW_PARAMS = {
    'bearer0':
    {
        'rate': 2,
        'rateSLO': 2,
        'delaySLO': .4,
    },
    'bulk':
    {
        'rate': 8,
        'rateSLO': 0,
        'delaySLO': 0.8,
    },
}

MODULE_COSTS = {
    # ingress
    "mac_table": .5,
    "type_check": .5,
    "dir_selector": .5,
    "vxlan_decap": .5,

    # egress
    "update_ttl": .5,
    "L3": .5,
    "update_mac_dl": .5,
    "ip_checksum_dl": .5,
    "update_mac_ul": .5,
    "ip_checksum_ul": .5,

    # bearers
    "dl_br_selector": 1,
    "dl_ue_selector": 1,
    "ul_br_selector": 1,
    "ul_ue_selector": 1,
    "dl_user_bp": 1,
    "setmd_dl": 1,
    "vxlan_encap": 1,
    "ip_encap": 1,
    "ether_encap": 1,
    "ul_user_bp": 1,
    "setmd_ul": 1,
}

MODULE_WORKERS = {
    # ingress
    "mac_table": 0,
    "type_check": 0,
    "dir_selector": 0,
    "vxlan_decap": 0,

    # egress
    "update_ttl": 2,
    "L3": 2,
    "update_mac_dl": 2,
    "ip_checksum_dl": 2,
    "update_mac_ul": 2,
    "ip_checksum_ul": 2,

    # bearers
    "dl_br_selector": 1,
    "dl_ue_selector": 1,
    "ul_br_selector": 1,
    "ul_ue_selector": 1,
    "dl_user_bp": 1,
    "setmd_dl": 1,
    "vxlan_encap": 1,
    "ip_encap": 1,
    "ether_encap": 1,
    "ul_user_bp": 1,
    "setmd_ul": 1,
}

# end of settings


class Module:
    """ Represents a packet processing module """

    def __init__(self, name: str, label: int, cost=-1, task=None, worker=None):
        """
        Parameters:
        name (str): Module name
        label (int): Module's id and label
        cost (int): Module execution cost
        task (dict): Task running the modules, parameters: label, name
        worker (dict): Worker running the module,
                       worker parameters: label, speed
        """
        self.name = name
        self.label = label
        self.cost = cost
        self.task = task or {'label': -1, 'name': ''}
        self.worker = worker or {'label': -1, 'speed': -1}
        self.flows = []

    def __repr__(self):
        return ("node [\n"
                "\tid {}\n"
                "\tlabel {}\n"
                "\tname \"{}\"\n"
                "\tcost {}\n"
                "\ttask {}\n"
                "\ttaskname \"{}\"\n"
                "\tworker {}\n"
                "\tworkerspeed {}\n"
                "\tflows\n"
                "\t[\n"
                "\t\t{}\n"
                "\t]\n"
                "]"
                .format(
                    self.label,
                    self.label,
                    self.name,
                    self.cost,
                    self.task['label'],
                    self.task['name'],
                    self.worker['label'],
                    self.worker['speed'],
                    self.__repr_flows().replace("\n", "\n\t\t")
                )
                )

    def __repr_flows(self) -> str:
        return "\n".join(("flow\n[\n"
                          "\tflowid {}\n"
                          "\tflowname \"{}\"\n"
                          "\tflowrate {}\n"
                          "\tflowrateSLO {}\n"
                          "\tflowdelaySLO {}\n"
                          "]"
                          .format(
                              f.label,
                              f.name,
                              f.params['rate'],
                              f.params['rateSLO'],
                              f.params['delaySLO'],
                          ))
                         for f in self.flows)


class Flow:
    """ Represents a flow """

    def __init__(self, name: str, modules=None, label=-1, params=None):
        """
        Parameters:
        name (str): Flow name
        modules (list): List of modules: Module
        label (int): Flow's id
        params (dict): Flow parameters: rate, rateslo, delayslo
        """
        self.name = name
        self.modules = modules or []
        self.label = label
        self.params = params or FLOW_PARAMS['bulk']

    def list_modules(self) -> list:
        """ Generates a list of module names in a flow"""
        return [module.name for module in self.modules]

    @staticmethod
    def get_flow_module_names(direction: str, bearer: int, user: int) -> str:
        """ Generates a string representation of flow modules list

        Parameters:
        direction (str): Flow direction (upstream/downstream). Either 'u' or 'd'.
        bearer (int): Bearer id
        user (int): User id

        Returns:
        a string of flow modules' name separated by ','

        """
        if direction == 'd':
            modules = ['mac_table', 'type_check', 'dir_selector', 'dl_br_selector',
                       f'dl_ue_selector_{bearer}', f'dl_user_bp_{user}_{bearer}',
                       f'setmd_dl_{user}_{bearer}', f'vxlan_encap_{user}_{bearer}',
                       f'ip_encap_{user}_{bearer}', f'ether_encap_{user}_{bearer}',
                       'update_ttl', 'L3', 'update_mac_dl', 'ip_checksum_dl']
        elif direction == 'u':
            modules = ['mac_table', 'type_check', 'dir_selector',
                       'vxlan_decap', 'ul_br_selector',
                       f'ul_ue_selector_{bearer}', f'ul_user_bp_{user}_{bearer}',
                       f'setmd_ul_{user}_{bearer}',
                       'update_ttl', 'L3', 'update_mac_ul', 'ip_checksum_ul']
        else:
            err_text = "Flow direction (upstream/downstream) must be either 'u' or 'd'"
            raise ValueError(err_text)

        return ','.join(modules)


class Config:
    """MGW config based on pipeline arguments """

    def __init__(self, nodes=None, arcs=None, flows=None, parameters=None):
        """
        Parameters:
        nodes (list): List of Module objects
        arcs (int): List of arc tuples
        flows (list): List of Flow objects

        """
        self.nodes = nodes or []
        self.arcs = arcs or []
        self.flows = flows or []
        self.parameters = parameters or {}

    def __create_gml_content(self) -> str:
        """ Create GML file content as a string """
        __dir = {"ul": " Uplink", "dl": " Downlink"}
        _direction = __dir.get(self.parameters['direction'].lower(), '')
        graph_params = "\n\t".join([
            f"name \"MobileGateWay{_direction}\"",
            "directed 1",
            f"Q {self.parameters['Q']}",
            f"B {self.parameters['B']}",
        ])
        nodes_str = "\n".join(("\t%s" % node).replace("\n", "\n\t")
                              for node in self.nodes)
        arcs_str = "\n".join("\tedge [\n\t\tsource {}\n\t\ttarget {}\n\t]".format(arc[0], arc[1])
                             for arc in self.arcs)
        gml_as_string = ("graph [\n"
                         "\t{}\n"
                         "{}\n"
                         "{}\n"
                         "]".format(graph_params, nodes_str, arcs_str))
        return gml_as_string

    def print_lgf(self):
        """ Print GML file content """
        print(self.__create_gml_content())

    def write_lgf(self, out_file: str):
        """Write GML content to file

        Parameters:
        out_file (str): out GML file

        """
        with open(out_file, 'w') as outfile:
            outfile.write(self.__create_gml_content())


def create_config(args: dict) -> Config:
    """ Create an MGW config based on pipeline arguments

    Parameters:
    args (dict): Pipeline arguments: user_num, bearer_num,
    bearer0_user, worker_number, worker_speed, direction (optional)

    Returns:
    config (Config): a config object with corresponding objects

    """
    user_num = args['usernum']
    bearer_num = args['bearernum']
    bearer0_user = args['bearer0user']
    worker_speed = args['worker_speed']
    direction = args.get('direction', '').lower()
    graph_params = {
        'Q': args['queue_size'],
        'B': args['batch_size'],
        'direction': args['direction'],
    }

    module_map = {}
    nodes = []

    common_node_names = [(name, name) for name in
                         ("mac_table", "type_check", "dir_selector",
                          "dl_br_selector", "vxlan_decap", "ul_br_selector",
                          "update_ttl", "L3", "update_mac_dl",
                          "ip_checksum_dl", "update_mac_ul", "ip_checksum_ul")]

    dl_node_names = ["dl_user_bp", "setmd_dl", "vxlan_encap", "ip_encap",
                     "ether_encap"]

    ul_node_names = ["ul_user_bp", "setmd_ul"]

    if direction == 'ul':
        bearer_node_names = ul_node_names
        common_node_names = [n for n in common_node_names if 'dl' not in n[0]]
    elif direction == 'dl':
        bearer_node_names = dl_node_names
        common_node_names = [n for n in common_node_names if 'ul' not in n[0]]
    else:
        bearer_node_names = ul_node_names + dl_node_names

    for name, w_name in common_node_names:
        task_name = 'egress'
        ingress_worker = MODULE_WORKERS['mac_table']
        if MODULE_WORKERS[w_name] == ingress_worker:
            task_name = 'ingress'
        module = Module(name, len(nodes),
                        cost=MODULE_COSTS[w_name],
                        task={'label': 0,
                              'name': task_name},
                        worker={'label': MODULE_WORKERS[w_name],
                                'speed': worker_speed})
        module_map[name] = module
        nodes.append(module)

    # note: tasks are assigned to each bearer0 user + each bearer
    # total number of bearer tasks are 2x num_bearer_tasks due to
    # separate ul/dl tasks;
    # ul tasks are numbered as num_bearer_tasks+i
    num_bearer_tasks = bearer0_user + bearer_num
    for bearer in range(bearer_num):
        if direction in ('ul', 'dl'):
            selector_names = [(f'{direction}_ue_selector_{bearer}',
                               f'{direction}_ue_selector')]
        else:
            selector_names = [(f'{name}_{bearer}', name)
                              for name in ('dl_ue_selector', 'ul_ue_selector')]
        for name, w_name in selector_names:
            task_id = bearer0_user + bearer
            cur_direction = 'dl'
            if 'ul' in w_name:
                cur_direction = 'ul'
                if not direction:
                    task_id += num_bearer_tasks
            task_name = f'bearer_{cur_direction}_{bearer}'
            worker_id = MODULE_WORKERS[w_name]
            if bearer == 0:
                # selector goes to ingress
                task_id = 0
                task_name = 'ingress'
                ingress_worker = MODULE_WORKERS['mac_table']
                worker_id = ingress_worker
            module = Module(name, len(nodes),
                            cost=MODULE_COSTS[w_name],
                            task={'label': task_id,
                                  'name': task_name},
                            worker={'label': worker_id,
                                    'speed': worker_speed})
            module_map[name] = module
            nodes.append(module)
        for user in range(user_num):
            if bearer == 0 and user >= bearer0_user:
                continue
            module_names = [(f'{name}_{user}_{bearer}', name)
                            for name in bearer_node_names]
            for name, w_name in module_names:
                cur_direction = 'dl_'
                if 'ul' in w_name:
                    cur_direction = 'ul_'
                if direction:
                    cur_direction = ''
                if bearer == 0:
                    task_id = user
                    task_name = f'bearer{bearer}_{cur_direction}user{user}'
                else:
                    task_id = bearer0_user + bearer
                    task_name = f'bearer{bearer}_{cur_direction}'.strip('_')
                if 'ul' in w_name and not direction:
                    task_id += num_bearer_tasks
                module = Module(name, len(nodes),
                                cost=MODULE_COSTS[w_name],
                                task={'label': task_id,
                                      'name': task_name},
                                worker={'label': MODULE_WORKERS[w_name],
                                        'speed': worker_speed})
                module_map[name] = module
                nodes.append(module)

    if direction in ('ul', 'dl'):
        directions = (direction[0],)
    else:
        directions = ('u', 'd')
    flows = []
    for bearer in range(bearer_num):
        for user in range(user_num):
            if bearer == 0 and user >= bearer0_user:
                continue
            for cur_dir in directions:
                bearer_name = "qos"
                if bearer > 0:
                    bearer_name = f"bulk{bearer}"
                short_dir = ""
                if len(directions) > 1:
                    short_dir = f"{cur_dir}l_"
                flow_name = f'user{user}_{short_dir}{bearer_name}'
                mod_names_str = Flow.get_flow_module_names(cur_dir,
                                                           bearer, user)
                modules = [module_map[name]
                           for name in mod_names_str.split(',')]
                # set flow parameters
                if bearer == 0:
                    flow_params = FLOW_PARAMS['bearer0']
                else:
                    flow_params = FLOW_PARAMS['bulk']
                flow = Flow(flow_name,
                            modules,
                            label=len(flows),
                            params=flow_params)
                flows.append(flow)
                for module in modules:
                    module.flows.append(flow)

    arc_set = set()
    for flow in flows:
        for source, target in zip(flow.modules, flow.modules[1:]):
            arc_set.add((source.label, target.label))
    arcs = list(arc_set)

    return Config(nodes=nodes,
                  arcs=arcs,
                  flows=flows,
                  parameters=graph_params)


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('--usernum', '-u', type=int, default=2,
                        help='Number of users')
    PARSER.add_argument('--bearernum', '-b', type=int, default=2,
                        help='Number of bearers')
    PARSER.add_argument('--bearer0user', '-bu', type=int, default=1,
                        help='Number of bearer0 users')
    PARSER.add_argument('--direction', '-d', type=str, default='',
                        choices=['ul', 'dl', ''],
                        help='Generate uplink/downlink part only. '
                        'Leaving empty results both uplink and downlink parts.')
    PARSER.add_argument('--worker_speed', '-W', type=float, default=40,
                        help='Worker speed')
    PARSER.add_argument('--queue_size', '-Q', type=int, default=1,
                        help='Queue size')
    PARSER.add_argument('--batch_size', '-B', type=int, default=1,
                        help='Packet batch size')
    PARSER.add_argument('--qos_rate', type=float,
                        default=FLOW_PARAMS['bearer0']['rate'],
                        help='Bearer0 (QoS) flow rate')
    PARSER.add_argument('--qos_rateslo', type=float,
                        default=FLOW_PARAMS['bearer0']['rateSLO'],
                        help='Bearer0 (QoS) flow rate SLO')
    PARSER.add_argument('--qos_delayslo', type=float,
                        default=FLOW_PARAMS['bearer0']['delaySLO'],
                        help='Bearer0 (QoS) flow delay SLO')
    PARSER.add_argument('--bulk_rate', type=float,
                        default=FLOW_PARAMS['bulk']['rate'],
                        help='Bulk flow rate')
    PARSER.add_argument('--bulk_rateslo', type=float,
                        default=FLOW_PARAMS['bulk']['rateSLO'],
                        help='Bulk flow rate SLO')
    PARSER.add_argument('--bulk_delayslo', type=float,
                        default=FLOW_PARAMS['bulk']['delaySLO'],
                        help='Bulk flow delay SLO')
    PARSER.add_argument('--outfile', '-o', type=str,
                        help='Output GML file')
    PARSER.add_argument('--perturbe_module_costs', '-p', action='store_true',
                        help='Perturbe module costs')
    PARSER.add_argument('--verbose', '-v', action='store_true',
                        help='Print GML content to stdout')
    ARGS_PARSED = PARSER.parse_args()

    if ARGS_PARSED.perturbe_module_costs:
        for module in MODULE_COSTS:
            MODULE_COSTS[module] = MODULE_COSTS[module] * random.random()

    FLOW_PARAMS = {
        'bearer0':
        {
            'rate': ARGS_PARSED.qos_rate,
            'rateSLO': ARGS_PARSED.qos_rateslo,
            'delaySLO': ARGS_PARSED.qos_delayslo,
        },
        'bulk':
        {
            'rate': ARGS_PARSED.bulk_rate,
            'rateSLO': ARGS_PARSED.bulk_rateslo,
            'delaySLO': ARGS_PARSED.bulk_delayslo,
        },
    }

    CONFIG = create_config(vars(ARGS_PARSED))

    if ARGS_PARSED.outfile:
        if ARGS_PARSED.verbose:
            CONFIG.print_lgf()
        CONFIG.write_lgf(ARGS_PARSED.outfile)
    else:
        CONFIG.print_lgf()

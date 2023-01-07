# Simulator for Real-Time NFV Scheduling on COTS Hardware in O-RAN

[Overview](#overview) | [Installation](#installation) | [Usage](#usage) | [License](#license)

_Disclaimer: The simulator is currently heavily work in progress!_

## Overview
A discrete time simulator to experiment with our real-time NFV scheduling controllers.

Simulator Workflow:
```
                                                   +--------------+
                                   +-------------->| System State |-------------+
                                   |               |  at Time t   |             |
                                   |               +--------------+             V
+------------+    t:=0     +--------------+                              +--------------+
|   Initial  |------------>|     Run      |                              | Run gradient |
| CPU shares |             | System Model |                              | optimization |
+------------+             +--------------+                              +--------------+
                                   ^                                            |
                                   |  t:= t+1    +---------------+              |
                                   +-------------|     New       |<-------------+
                                                 | task weights  |
                                                 +---------------+
```

## Installation

### Dependencies

* [Python](https://www.python.org/downloads/) (>=3.6)
* Python packages listed in [requirements.txt](requirements.txt)

## Usage

The simulator contains many preset scenarios. Please jump to [Run Simulations](#run-simulations). If you are interested in fine-tuning the simulator or adding new pipelines, please refer to [Config](#config).

### Config

The simulator reads configurations from command line arguments and from its settings file. For details of the simulator parameters, please refer to the paper.

Pipeline configurations are stored in the [inputs](./inputs) folder.

### Adjust defaults and set constants
The simulator reads the configratuion file from [lib/settings.py](lib/settings.py).

### Add new pipelines
To add new pipeline, simply create a `.gml` file describing the new pipeline. The recommendation is to store these pipeline configurations in the [`inputs`](./inputs) folder.

#### Generate MGW configs
The mobile gateway (MGW) is a complex pipeline with large number of modules and edges. To ease creating new configurations, an [MGW](https://github.com/hsnlab/tipsy/blob/master/doc/README.mgw.org) config generator script is provided. This script generates `.gml` files for the simulator based on an [MGW implementation in BESS](https://github.com/hsnlab/tipsy/blob/master/bess/mgw.bess). For parameters, please refer to the help: `python3 generate_mgw_config.py -h`


### Run Simulations
The simulator is implemented in Python, and its entrypoint is [`simulator.py`](simulator.py). Almost all simulator parameters can be adjusted by command line parameters. For details of the parameters, please refer to the paper. To get a list of parameters, please refer to the help: `python3 simulator.py -h`

An example to simulate the configuration of the example pipeline (fork) with back-pressure enabled for `20` rounds, and save simulation results to `results/optimize_out.txt` (after simulation, the plot will be shown):
```console
python3 simulator.py -l INFO -p -i inputs/example_basic_back_pressure.gml -o results/optimize_out.txt -r 20
```

### Plot Results
The simulator draws plots at the end of its execution. Simulation plots can be drawn using a stand-alone program as well:

```console
python3 plot_results.py <simulator_output_csv>
```

Additional useful features:
- to print the dataset constructed from the simulator CSV: `-v`
- to set a custom plot title: `-t <title>`
- to save the plot in PNG: `-o <outfile>`

## License

Licensed under [GPLv3+](/LICENSE).

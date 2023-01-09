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
                                   |  t:= t+1      +--------------+             |
                                   +---------------|     New      |<------------+
                                                   | task weights |
                                                   +--------------+
```

## Installation

### Dependencies

* [Python](https://www.python.org/downloads/) (>=3.6)
* Python packages listed in [requirements.txt](requirements.txt)

## Usage

The simulator contains many preset scenarios. Please jump to [Run Simulations](#run-simulations). If you are interested in fine-tuning the simulator or adding new pipelines, please refer to [Config](#config).
To reproduce figures in the paper, check [Reproduce Figures of the Paper](#reproduce-figures-of-the-paper).


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


### Reproduce Figures of the Paper

#### Figure 5: Effect of parameter α

Parameter α is responsible for weighing in the possible delay SLO violations, measured on the _fork_ pipeline.

| Figure  | Command |
| :---    | :---    |
| Fig. 5a | `python3 simulator.py --infile ./inputs/example_basic_new_estimate.gml --alpha 0.05 --delta 0.01 --rho_roughness 0.05 --rounds 50 --epsilon 1e-05 --plot` |
| Fig. 5b | `python3 simulator.py --infile ./inputs/example_basic_new_estimate.gml --alpha 0.2 --delta 0.01 --rho_roughness 0.025 --rounds 50 --epsilon 1e-05 --plot` |
| Fig. 5c | `python3 simulator.py --infile ./inputs/example_basic_new_estimate.gml --alpha 0.05 --delta 0.01 --rho_roughness 0.025 --rounds 50 --epsilon 1e-05 --plot` |

#### Figure 6: Controller with simultaneously satisfiable delay and rate SLOs

Controller on pipelines _taildrop_ and _MGW_ accompanied with simultaneously satisfiable delay and rate SLOs, respectively. With α = 1, the controller found a feasible solution in 15 control periods in both cases.

| Figure  | Command |
| :---    | :---    |
| Fig. 6a | `python3 simulator.py --infile ./inputs/taildrop.gml --alpha 1 --delta 0.01 --rho_roughness 0.025 --rounds 50 --epsilon 1e-05 --plot` |
| Fig. 6b | `python3 simulator.py --infile ./inputs/mgw_default.gml --alph 1 --delta 0.01 --rho_roughness 0.025 --rounds 20 --epsilon 1e-05 --realloc_interval 10 --plot` |

#### Figure 8: Task migration results

The reallocation controller runs in every 10-th control period.

| Figure  | Command |
| :---    | :---    |
| Fig. 8a | `python3 simulator.py --infile ./inputs/taildrop_2workers.gml --alpha 1 --delta 0.01 --rho_roughness 0.025 --rounds 20 --epsilon 1e-05 --realloc_interval 10 --plot` |
| Fig. 8b | `python3 simulator.py --infile ./inputs/taildrop_realloc_optimize.gml --alpha 1 --delta 0.01 --rho_roughness 0.01 --rounds 20 --epsilon 1e-05 --realloc_interval 10 --plot` |
| Fig. 8c | `python3 simulator.py --infile ./inputs/example_basic_realloc.gml --alpha 1 --delta 0.01 --rho_roughness 0.025 --rounds 20 --epsilon 1e-05 --realloc_interval 10 --plot` |
| Fig. 8d | `python3 simulator.py --infile ./inputs/taildrop_realloc_optimize_7.gml --alpha 1 --delta 0.01 --rho_roughness 0.01 --rounds 75 --epsilon 1e-05 --realloc_interval 10 --plot` |
| Fig. 8e | `python3 simulator.py --infile ./inputs/mgw_default_reallocation.gml --alpha 1 --delta 0.01 --rho_roughness 0.025 --rounds 20 --epsilon 1e-05 --realloc_interval 10 --plot` |


## License

Licensed under [GPLv3+](/LICENSE).

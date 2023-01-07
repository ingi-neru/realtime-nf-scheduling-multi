# Measurement to Validate Task Delay Estimate

This measurement monitors tasks arranged as the _fork_ pipeline:
```
                +--------+
                |        |
             -->|  Task  |
            /   |        |
+--------+ /    +--------+
|        |/
|  Task  |
|        |\
+--------+ \    +--------+
            \   |        |
             -->|  Task  |
                |        |
                +--------+

                   ...
```

## Requirements

* [Our BESS fork (our-plugins branch)](https://github.com/levaitamas/bess/tree/our-plugins)
* [Python3](https://www.python.org/downloads/)
 * [pandas](https://pandas.pydata.org/)
 * [matplotlib](https://matplotlib.org/)

## Execution

1. Collect measurement data

Parameters:
 - `num_tasks`: number of egress tasks
 - `meas_interval`: measurement time in seconds

```sh
cd bess/bessctl
 ./bessctl run local/dtf-estimate-check meas_interval=10,num_tasks=2 > /tmp/out.csv
```

2. Plot measurement data
```sh
./plot_dtf_estimate_check.py /tmp/out.csv
```

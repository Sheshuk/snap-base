# SuperNova Async Pipeline: base package

This package contains base for asynchronous real-time data analysis pipeline.
It was designed for the supernova neutrino signal detection.

## Features
* Running chains of generators and functions asynchronously.
* Computationally heavy/blocking code is run in parallel threads/processes.
* Pipeline is configured in a `yaml` file, where the steps are assembled and parameters are set.
* Branching support: data can be fed to parallel chains for various processing.
* ZeroMQ interface to connect running nodes with each other.

## Installation

```shell
pip install snap-base
```

## Defining the pipeline
The pipeline definition consist of

1. A python module (or modules) where all the processing steps should be defined
2. `yaml` configuration file, defining how the data should flow through these steps.

For more details see: [Pipeline_elements](Pipeline_elements.md)

While this package defines some basic functions, like sending and receiving data via ZMQ or running analysis step in parallel processes,
all other needed functions will need to be defined by user in the python package.

Package [snap-combine](https://github.com/Sheshuk/snap-combine) contains more utility functions for the supernova neutrino signals combinations.

## Running

Go to the directory where your 
Run the node named `node_name` from `config.yml`:
```shell
snap config.yml -n node_name
```

# Example

Put the example module [example.py](example/example.py) and configuration [example_cfg.yml](example/example_cfg.yml) in a directory.

Run the example node with branching:
```shell
snap example_cfg.yml -n node_branching
```
And you should see the output of the generated random walk , and it's analysis in two branches.


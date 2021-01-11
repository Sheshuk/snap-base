# SuperNova Async Pipeline: base package

This package contains base for asynchronous pipeline for supernova detection.

## Installation

Install `snap-base` package
```shell
pip install snap-base
```

## Configuration

### Define pipeline elements
While this package defines some basic functions, like sending and receiving data via ZMQ or running analysis step in parallel processes,
all other needed functions will need to be defined by user in the python package.

Package [snap-combine](https://github.com/Sheshuk/snap-combine) contains more utility functions for the supernova signals combinations and can be used as an example.

### Create the pipeline configuration file
Create yaml configuration file, describing your pipelines.
This is where you link the elements with given parameters to the analysis chain(s).
*TODO: describe configuration format*

## Running

Go to the directory where your 
Run the node named `node_name` from `config.yml`:
```shell
snap -c config.yml -n node_name
```

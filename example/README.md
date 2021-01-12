# Usage example
SNAP allows user to construct pipelines from the user-defined steps and methods of the data processing. 

## Asynchronous pipeline

The goal of the pipeline is to process the input data in several consequtive steps with minimal latency. 
In most cases, when handling the data in real time, some steps require idle periods of waiting for the data to come from the upstream sourses. 
SNAP uses python [asyncio](https://docs.python.org/library/asyncio.html) approach to make these waits asynchronous, so that one part of the pipeline can continue processing, while the other is waiting.


# Pipeline structure

Each pipeline application is defined as [node](#node), which consists of [chains](#chain), which is composed of [sources](#source) and [steps](#step) processing the [data](#data).


#### Data portion
Pipeline processes data in portions.
This portion can be any python object - a number, tuple, string, function, etc.
Data is produced by the [source](#source) and processed in the [steps](#step).

#### Source
An asynchronous (or synchronous) generator producing [data](#data)

Simple example of a [source](#source) from [example.py](example/example.py):

```python
#source from async generator
async def gen_timestamp(delay=1):
"""generate current timestamps with given delay"""
    while True:
        await asyncio.sleep(delay)
        yield datetime.datetime.now()
```
In practical cases it can be yielding the data when it arrives in the file or via network.


### Step
Step defines any data manipulation. 
Steps can be vaguely classified into [transformations](#transformation), [filters](#filter) and [buffers](#buffer).

In the configuration file steps are provided as a list in the `steps:` section inside the [chain](#chain) definition.

#### Transformation
It's a [step](#step) that manipulates one data portion, and returns the result, which will be fed to the next step.

Can be just a function on the data, like this example
```python
#function without parameters
def dump(d):
    print(f'DUMP: {d}')
    return d
```
and referenced in the configuration file as 
```yml
steps:
    - foo.bar.dump
```

But if the processing function needs configurable parameters, it should be defined as a functor, or a function of parameters, returning the function of the data, like in this example:

```python
#function with parameters
def dump(prefix="DUMP"):
    def _f(d):
        print(f'{prefix} {d}')
        return d
    return _f
```
and described in the configuration with parameters:
```yml
steps:
    - foo.bar.dump: {prefix: "Here's what I got:"}
```
> :warning: Arguments are passed to function/functor constructor as **keyword** args

### Filter
Here the filter is a [step](#step) that receives all the data portions, but produces results only after some of them.

It can be defined as an asynchronous coroutine:
```python
# filter example: corountine
async def positive(source):
    """ yield positive values """
    async for d in source:
        if(d>val): 
            yield d
```
and described in the configuration as:
```yml
steps:
    - foo.bar.positive
```

or as a function, producing coroutine, if the algorithm needs parameters:

```python
# filter example with parameters
def threshold(val=0):
    """ yield values above 'val' """
    async def _f(source):
        async for d in source:
            if(d>val): 
                yield d
    return _f
```
and described in the configuration as:
```yml
steps:
    - foo.bar.threshold: {val: 1}
```

### Buffer

A [step](#step) which processes the data, but the input loop from the output loop. 


### Chain

Chain defines a single pipeline, getting the data from its [source](#source) and processing it in the [steps](#step) one by one, and optionally forwarding it to one or several other chains (targets).
Chain is defined in the configuration file and should consist of a *name*, [source](source), [steps](step) and  *targets*(optional)


### Node
A single python process, which consists of one or more [chains](#chain) and runs them in the loop.




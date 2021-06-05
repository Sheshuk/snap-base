Asynchronous pipeline
=====================

The goal of the pipeline is to process the input data in several consequtive steps with minimal latency. 
In most cases, when handling the data in real time, some steps require idle periods of waiting for the data to come from the upstream sourses. 
SNAP uses python `asyncio <https://docs.python.org/library/asyncio.html>`_ approach to make these waits asynchronous, so that one part of the pipeline can continue processing, while the other is waiting.

Each pipeline application is defined as :ref:`node`, which consists of one or several :ref:`chains<chain>`, which is composed of :ref:`source` and one or several :ref:`steps<step>` processing the :ref:`data-portion`.

This section defines the basic terms, used in SNAP, and how to use them:


.. _node:

Node
^^^^

A single python process, which consists of one or more :ref:`chain` and runs all of them simulatneously (asynchronously).

It is defined in the configuration file as a mapping of node name and it's chains:

.. code-block:: yaml

    <node name>:
        <chain name1>:
            #chain1 configuration here
        <chain name2>:
            #chain2 configuration here

where ``<node name>`` is a name of this node, describing it's purpose. 
This name will be used, when running the snap program with ``snap --node <node name>`` option)


:Note: Node names within one file must be different.
 Chain names within the node must be different.

.. _chain:

Chain
^^^^^^^^^^^^^^^^

Chain defines a single pipeline, getting the data from its :ref:`source` and processing it in the :ref:`step` one by one, and optionally forwarding it to one or several other chains (targets).

Chain is defined in the configuration file and consist of:

:<chain name>: any name describing the chain purpose

:source:
    Section with a :ref:`source` element.
    If missing, the chain is expected to receive data from another chain (if it's listed in another chain's ``to`` section).

:steps:
    Section with a list of one or more :ref:`step` elements.
    If missing, then the chain will just draw data from source and pass to the targets.

:to:
    Section with one or more other :ref:`chain` names within the same node, where the output of the last step should be forwarded. 
    If missing, then the data from last step is not forwarded.


.. code-block:: yaml

    <chain name>:
        source:
            <source element>
        steps:
            - <step element 1>
            - <step element 2>
        to: [<chain_name1>, <chain_name2>]




.. _data-portion :

Data portion
^^^^^^^^^^^^^
Pipeline processes data in portions.
This portion can be any python object - a number, tuple, string, function, etc.
Data is produced by the :ref:`source` and processed in the :ref:`step`.

.. _source :

Source
^^^^^^^
An asynchronous (or synchronous) generator producing :ref:`data-portion`

Simple example of a :ref:`source`

.. code-block:: python

    #source from async generator
    async def gen_timestamp(delay=1):
    """generate current timestamps with given delay"""
        while True:
            await asyncio.sleep(delay)
            yield datetime.datetime.now()

In practical cases it can be yielding the data when it arrives in the file or via network.

.. _step :

Step
^^^^^^^^^^^^^^^^
Step defines any data manipulation. 
Steps can be vaguely classified into :ref:`transformation`, :ref:`filter` and :ref:`buffer`.

In the configuration file steps are provided as a list in the `steps:` section inside the :ref:`chain` definition.

.. _transformation :

Transformation
""""""""""""""
It's a :ref:`step` that manipulates one data portion, and returns the result, which will be fed to the next step.

Can be just a function on the data, like this example

.. code-block:: python

    #function without parameters
    def dump(d):
        print(f'DUMP: {d}')
        return d

and referenced in the configuration file as 

.. code-block:: yaml

    steps:
        - foo.bar.dump


But if the processing function needs configurable parameters, it should be defined as a functor, or a function of parameters, returning the function of the data, like in this example:

.. code-block:: python

    #function with parameters
    def dump(prefix="DUMP"):
        def _f(d):
            print(f'{prefix} {d}')
            return d
        return _f

and described in the configuration with parameters:

.. code-block:: yaml

    steps:
        - foo.bar.dump: {prefix: "Here's what I got:"}

:Note: Arguments are passed to function/functor constructor as *keyword* args

.. _filter:

Filter
""""""""""""""
Here the filter is a :ref:`step` that receives all the data portions, but produces results only after some of them.

It can be defined as an asynchronous coroutine:

.. code-block:: python

    # filter example: corountine
    async def positive(source):
        """ yield positive values """
        async for d in source:
            if(d>val): 
                yield d

and described in the configuration as:

.. code-block:: yaml

    steps:
        - foo.bar.positive


or as a function, producing coroutine, if the algorithm needs parameters:

.. code-block:: python
   
    # filter example with parameters
    def threshold(val=0):
        """ yield values above 'val' """
        async def _f(source):
            async for d in source:
                if(d>val): 
                    yield d
        return _f

and described in the configuration as:

.. code-block:: yaml

    steps:
        - foo.bar.threshold: {val: 1}


.. _buffer:

Buffer
""""""""""""""

"Buffer" is a :ref:`step` which processes the data, but the input event loop is decoupled from the output loop. 
An example could be buffering data, and producing the accumulated data every 10 seconds.

A buffer object is defined as a python class, implementing `async def put` and `async def get` methods.
Example:

.. code-block:: python

    class Buffer:
        def __init__(self, buffer_time=10):
            """object to accumulate the data in the time bins"""
            self.data = []
            self.buffer_time = buffer_time
        async def put(self, data):
            self.data+=[data]

        async def get(self):
            #will yield the data array every approx every buffer_time
            await asyncio.sleep(self.buffer_time)
            res = self.data
            self.data = []
            return res


And in configuration file is defined as (if ``Buffer`` is inside ``foo.bar`` python module):

.. code-block:: yaml

    steps:
        - foo.bar.Buffer: {buffer_time: 10} 

:Note: A buffer can also be used as a :ref:`source` of a chain. In that case, if the data flows from another chain, it will be `put` in the buffer.



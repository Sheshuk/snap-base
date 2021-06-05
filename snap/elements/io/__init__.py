""" Collection of IO interfaces 

Interfaces provide similar functions: 

* :code:`send(data)`
    A processing :term:`step`, which sends the given data object, and also returns the data unchanged, so one can chain several senders/processing steps

* :code:`recv()`
    A data :term:`source`, which yields the data objects once they are received

"""

from . import hop,zmq


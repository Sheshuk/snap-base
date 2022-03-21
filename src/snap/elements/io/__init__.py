""" Collection of IO interfaces 

Interfaces provide similar functions: 

* :code:`send(data)`
    A processing :term:`step`, which sends the given data object, and also returns the data unchanged, so one can chain several senders/processing steps

* :code:`recv()`
    A data :term:`source`, which yields the data objects once they are received

"""
import asyncio
from . import queue, zmq
try:
    from . import hop
except ImportError:
    pass

def get_provider(address: str):
    if '://' not in address:
        return queue
    else:
        transport = address.split('://',1)[0]
        if transport in ['queue','']:
            return queue
        elif transport in ['tcp','udp','ipc','inproc','pgm','epgm']:
            return zmq
        elif transport=='kafka':
            return hop
        else:
            raise RuntimeError(f'Unknown transport "{transport}" for {address}')

def recv(address: str):
    return get_provider(address).recv(address)
    
def send(address: list[str]):
    return get_provider(address[0]).send(address)


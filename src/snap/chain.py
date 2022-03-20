import asyncio
import inspect

import logging
from collections.abc import AsyncGenerator, Iterable
from typing import Any, Optional, NewType
from snap.elements.io import queue as q

logger = logging.getLogger(__name__)

def _wrap_function(fun):
    async def _f(source):
        async for d in source:
            yield fun(d)
    return _f

def _is_function(a):
    return callable(a)
def _is_asyncgenfunc(a):
    return inspect.isasyncgenfunction(a)
def _is_asyncgen(a):
    return inspect.isasyncgen(a)
def _is_buffer(a):
    return hasattr(a,'put') and inspect.iscoroutinefunction(a.put) \
       and hasattr(a,'get') and inspect.iscoroutinefunction(a.get)

def wrap(a):
    """create async gen function from object a"""
    if _is_asyncgenfunc(a):
        return a
    elif _is_function(a):
        return _wrap_function(a)
    else:
        raise TypeError(f'{a} has wrong type {type(a)}')

class Chain:
    def __init__(self, name:str,
                       source: AsyncGenerator|None = None,
                       *elements: Iterable
                       ):
        """Create chain of processing elements
        
        parameters:
            elements(iterable) - each element should be either:
              - an async gen function, with async generator as input source (parameter)
               
            source (async gen) - generator providing the input data

            targets (iterable) - collection of buffer objects, where the results will be pushed.
                      If empty, the data output after the last element is lost
            name - the chain name, to provide  meaningful output
        """
        if source:
            self.source = source
        else:
            self.source = q.recv(name)
        self.elements = list(elements)
        self.name = name

    def build(self):
        logger.info(f'Building chain: {self.name}')
        gen = self.source
        for e in self.elements:
            gen = e(gen)
        self.gen = gen

    async def run(self):
        self.build()
        logger.info(f'Starting chain: {self.name}')
        try:
            async for d in self.gen:
                await asyncio.sleep(0)
        except asyncio.CancelledError as e:
            logger.info(f'Stopping chain: {self.name}')
        except Exception as e:
            raise RuntimeError(f'Failed run in chain {self.name}')

def make_chains(elements, source=None,  name="Chain"):

    chain = Chain(name, source)
    chains = [chain]
    for e in elements:
        if _is_buffer(e):
            new_name = q.register(e,name=f'{name}.{e.__class__.__name__}')
            chain.elements.append(q.send([new_name]))
            chain = Chain(name=new_name, source=q.recv(new_name))
            chains.append(chain)
        else:
            chain.elements.append(wrap(e))

    return chains

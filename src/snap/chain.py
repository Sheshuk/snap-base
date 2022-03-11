import asyncio
import inspect

import logging
from collections.abc import AsyncGenerator, Generator, Iterable
from typing import Any, Optional, NewType

logger = logging.getLogger(__name__)

def _wrap_function(fun):
    async def _f(source):
        async for d in source:
            yield fun(d)
    return _f

def _wrap_buffer(buf):
    async def _f(source=None):
        while True:
            yield await buf.get()
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

def wrap_source(a):
    """create async gen from object a"""
    if _is_asyncgen(a):
        return a
    elif _is_buffer(a):
        return _wrap_buffer(a)(source=None)
    else:
        raise TypeError(f'{a} has wrong type {type(a)}')


class Element:
    def __init__(self, f):
        self.gen = wrap(f)

    def __call__(self, source: AsyncGenerator[Any]) -> AsyncGenerator[Any]:
        return self.gen(source)

class Chain:
    all_chains: dict[str,'Chain'] = {} 
    def __init__(self, name:str, 
                       source: Element,
                       *elements: Iterable[Element]
                       ):
        """Create chain of processing elements
        
        parameters:
            elements(iterable) - each element should be either:
              - an async gen function, with async generator as input source (parameter)
              - a buffer object (the one providing 'async get()' and 'async put(data)' methods)
              - a callable f(data) -> result, operating on each data entry
              
            source (async gen) - generator providing the input data

            targets (iterable) - collection of buffer objects, where the results will be pushed.
                      If empty, the data output after the last element is lost
            name - the chain name, to provide  meaningful output
        """
        self.source = source
        self.elements = list(elements)
        self.name = name
        self.all_chains[name] = self

    def build(self):
        logger.info(f'Building chain: {self.name}')
        self.gen = wrap_source(self.source)
        for e in self.elements:
            self.gen = e(self.gen)

    async def put(self, data):
        await self.source.put(data)

    async def run(self):
        self.build()
        logger.info(f'Starting chain: {self.name}')
        try:
            async for d in self.gen:
                await asyncio.sleep(0)
        except asyncio.CancelledError as e:
            logger.info(f'Stopping chain: {self.name}')

def to_chain(address):
    async def _f(source):
        target = Chain.all_chains[address]
        async for data in source:
            await target.put(data)
            yield data
    return _f


def make_chains(elements, source=None,  name="Chain"):

    source = source or asyncio.Queue()
    chain = Chain(name, source)
    chains = [chain]
    for e in elements:
        if _is_buffer(e):
            chain = Chain(name=f"{name}.{len(chains):02d}", source=e)
            chains[-1].elements.append(to_chain(chain.name))
            chains.append(chain)
        else:
            chain.elements.append(wrap(e))

    return chains



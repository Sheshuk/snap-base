import asyncio
from typing import Dict
import logging

__registry: Dict[str,asyncio.Queue] = dict()

def register(obj:object = asyncio.Queue(), name:str|None=None)->str:
    """Register a new object *obj* with preferred name.
    If the name is taken, use {name}.01, {name}.02 etc.

    Returns:
    -------
    name in registry
    """
    name0 = name or obj.__class__.__name__
    name = name0
    n = 0
    while name in _registry:
        n+=1
        name = f'{name0}.{n:02d}'
    __registry[name] = obj
    return name

def strip_name(name:str):
    _prefix = 'queue://'
    if name.startswith(_prefix):
        name = name.lstrip(_prefix)
    return name

async def recv(address:str):
    name = strip_name(address)
    if name not in _registry:
        __registry[name] = asyncio.Queue()

    q = __registry[name]
    print(f'Reading queue "{name}"')
    logging.warning(f'Available keys are: {list(__registry.keys())}')
    while True:
        yield await q.get()

def send(address:list[str]):
    async def _f(source):
        try:
            targets = [__registry[strip_name(a)] for a in address]
        except KeyError as e:
            logging.error(f'Available keys are: {list(__registry.keys())}')
            raise
        async for data in source:
            await asyncio.gather(*[t.put(data) for t in targets])
            yield data
    return _f



import asyncio
from typing import Dict

_registry: Dict[str,asyncio.Queue] = dict()

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
    _registry[name] = obj
    return name

def from_queue(name):
    if name not in _registry:
        _registry[name] = asyncio.Queue()

    q = _registry[name]
    async def _f():
        while True:
            yield await q.get()
    return _f

def to_queue(name):
    async def _f(source):
        target = _registry[name]
        async for data in source:
            await target.put(data)
            yield data
    return _f



import asyncio
import inspect

def _wrap_function(fun):
    async def _f(source):
        async for d in source:
            yield fun(d)
    return _f

def _wrap_buffer(buf):
    async def _get_data(source):
        #task to read data, when it's available
        async for d in source:
            await buf.put(d)
            
    async def _f(source=None):
        if source is not None:
            #run reading task
            task = asyncio.create_task(_get_data(source))
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
    elif _is_buffer(a):
        return _wrap_buffer(a)
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

        
async def chain(*elements, source, targets=[]):
    """Create chain of processing elements
    
    parameters:
        elements(iterable) - each element should be either:
          - an async gen function, with async generator as input source (parameter)
          - a buffer object (the one providing 'async get()' and 'async put(data)' methods)
          - a callable f(data) -> result, operating on each data entry
          
        source (async gen) - generator providing the input data

        targets (iterable) - collection of buffer objects, where the results will be pushed.
                  If empty, the data output after the last element is lost
        
    returns:
        awaitable, which can be run as an asynchronous task
    """
    gen = wrap_source(source)
    #chain all the elements
    for e in elements:
        gen = wrap(e)(gen)
    #run the chain
    async for d in gen:
        #send data to targets
        for t in targets:
            await t.put(d)

from .queue import register, _registry, from_queue, to_queue
import pytest

def test_register():
    n1 = register()
    n2 = register()
    n3 = register(name='test')
    assert n1=='Queue'
    assert n2=='Queue.01'
    assert n3=='test'
    assert list(_registry.keys())==[n1,n2,n3]

async def source_from_array(data):
    for d in data:
        yield d
    yield None

async def gather_all(source):
    res = []
    async for d in source:
        if d is None:
            break
        res+=[d]
    return res

@pytest.mark.asyncio
async def test_put_get():
    name='test1'
    data = [1,2,3]
    getter = from_queue(name)
    putter = to_queue(name)
    source = source_from_array(data)
    #put the data
    data1= await gather_all(putter(source))
    assert data1 == data
    print(data1)
    
    data2= await gather_all(getter())
    assert data2 == data
    print(data2)

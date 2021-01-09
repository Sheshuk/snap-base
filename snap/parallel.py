from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
import logging
import asyncio
logger = logging.getLogger(__name__)

class Parallel:
    execs = { 
             'thread': ThreadPoolExecutor,
             'process': ProcessPoolExecutor
             }   
    def __init__(self, function, executor='thread', max_workers=None):
        self.func= function
        self.exe = self.execs[executor](max_workers=max_workers)
        self.tasks = set()
        self.results = []
        self.has_tasks = asyncio.Event()
    async def put(self, data):
        t = asyncio.get_event_loop().run_in_executor(self.exe,
                                                     self.func, 
                                                     data)
        self.tasks.add(t)
        self.has_tasks.set()
        logger.debug(f'Pending {len(self.tasks)} tasks: {self.tasks}')
    async def get(self):
        while not self.results:
            await self.has_tasks.wait()
            logger.debug(f'waiting for results from {len(self.tasks)} task')
            completed,pending = await asyncio.wait(self.tasks, 
                                                   return_when=asyncio.FIRST_COMPLETED)
            logger.debug(f'completed:{len(completed)}, pending: {len(pending)}')
            self.results = [c.result() for c in completed]
            self.tasks-=completed
            if not self.tasks:
                self.has_tasks.clear()

        logger.debug(f'results:{self.results}')
        return self.results.pop()

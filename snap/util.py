from tqdm.asyncio import tqdm

def ticker(**kwargs):
    async def _f(source):
        with tqdm(source, **kwargs) as t:
            async for d in t:
                yield d
    return _f

def meter(**kwargs):
    t = tqdm(**kwargs)
    def _f(d):
        val = d.zs.max()
        t.n = val
        t.update(0)
        return d
    return _f

import asyncio
def run_shell(cmd):
    async def _run(data):
        print(f"Run!")
        run_cmd = cmd.format(**data)
        print(f"Command to run: {run_cmd}")
        proc = await asyncio.create_subprocess_shell(run_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
                )
        stdout, stderr = await proc.communicate()
        if stdout:
            print(f'[stdout]\n{stdout.decode()}')
        if stderr:
            print(f'[stderr]\n{stderr.decode()}')
        await proc.wait()
        return stdout.decode()
    return _run

def dump_to_file(fname):
    with open(fname,'w') as f:
        f.write('#------\n')
    def _f(data):
        with open(fname,'a') as f:
            f.write(repr(data)+'\n')
        return data
    return _f

import logging

def log(logger="snap", fmt="{}"):
    theLogger = logging.getLogger(logger)
    def _f(data):
        theLogger.info(fmt.format(data))
        return data

    return _f



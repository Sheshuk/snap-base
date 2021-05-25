"""
Utility functions for monitoring and output
"""
from tqdm.asyncio import tqdm

def ticker(**kwargs):
    """ 
    A monitoring :term:`step`.
    Display a `tqdm` progress bar, which is incremented with every data portion.
    For full arguments list see `tqdm documentation <https://github.com/tqdm/tqdm#documentation>`_   
    
    Keyword Args:
        desc (str)
            Prefix for the progressbar description 
        total (int or float, optional)
            The number of expected iterations
            (displays progressbar until this number is reached, becomes a ticker afterwards)
    :Input:
        data (anything)
    :Output:
        data unchanged
 
    """
    async def _f(source):
        with tqdm(source, **kwargs) as t:
            async for d in t:
                yield d
    return _f

def meter(**kwargs):
    """ 
    A monitoring :term:`step`.
    Display a `tqdm` progress bar, where the progress is set by the incoming data (must be float)
    For full arguments list see `tqdm documentation <https://github.com/tqdm/tqdm#documentation>`_
    
    Keyword Args:
        desc (str)
            Prefix for the progressbar description 
        total (int or float, optional)
            Maximal value

    :Input:
        data (float): A value to be displayed
    :Output:
        data unchanged
    """
 
    t = tqdm(**kwargs)
    def _f(d):
        t.n = d
        t.update(0)
        return d
    return _f

import asyncio
def run_shell(cmd):
    """
    A processing :term:`step`.
    Run shell command every time the `data` arrives.

    Args:
        cmd (str):
            A command to run. 
            If cmd is a template, like ``echo {foo} {bar}``, data should contain keys "foo" and "bar"

    :Input:
        data(dict) will be used to define the command:
        :code:`run_cmd = cmd.format(**data)`

    :Output: 
        (str) stdout of the executed command
    """
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
    """ 
    A processing :term:`step`.
    Save the incoming data to a text file

    Args:
        fname(str)
            A file name. File is opened for writing.
    :Input:
        data to be written as string representation :code:`repr(data)`
    :Output:
        data unchanged
    """
    with open(fname,'w') as f:
        f.write('#------\n')
    def _f(data):
        with open(fname,'a') as f:
            f.write(repr(data)+'\n')
        return data
    return _f

def dump(prefix="DUMP"):
    """ 
    A processing :term:`step`.
    Print the incoming data to stdout with given prefix

    Args:
        prefix(str)
            String prefix before each output
    :Input:
        data: to be written as string representation :code:`repr(data)`
    :Output:
        data unchanged
    """
    def _f(d):
        print(f'{prefix} {d}')
        return d
    return _f


import logging

def log(logger="snap", fmt="{}"):
    theLogger = logging.getLogger(logger)
    def _f(data):
        theLogger.info(fmt.format(data))
        return data
    return _f



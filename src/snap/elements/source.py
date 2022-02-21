"""
Data sources
============
"""
import sys, asyncio
from concurrent.futures import ThreadPoolExecutor
import numpy as np

async def read_txt(fname:str, size:int, columns:dict, delay:float=0):
    """
    Data :term:`source` from a text file/input stream.
    Watch the given file and read the new data in the text table format

    Args:
        fname
            Path to file to read or "stdin" for reading from standard input.
            File should contain text data organized in space separated columns, like::
                
                a1 b1 c1
                a2 b2 c2
                a3 b3 c3
                ...

        size
            Maximal number of rows to read.
        columns
            Dict of format :code:`"val_name": column_number`
        delay
            Minimal delay between reading each data chunk, in seconds.

    Yields: 
        dict with data organized by the columns with column names as key
    """
    fo = sys.stdin if fname=='stdin' else open(fname)
    with fo as f:
        loop = asyncio.get_event_loop()
        def do_read():
            res = np.loadtxt(f, usecols = columns.values(), unpack=True,max_rows=size)
            return dict(zip(columns, res))
        with ThreadPoolExecutor() as exe:
            while f:
                yield await loop.run_in_executor(exe, do_read)
                await asyncio.sleep(delay)


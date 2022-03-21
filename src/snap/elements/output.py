"""
Steps for output
==========================

"""
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
            f.write(f'{data}\n')
        return data
    return _f

def dump(prefix="DUMP", rewrite=False):
    """ 
    A processing :term:`step`.
    Print the incoming data to stdout with given prefix

    Args:
        prefix(str)
            String prefix before each output
        rewrite(bool)
            If true, will end this line with `\\r`, so it will be overwritten
    :Input:
        data: to be written as string representation :code:`repr(data)`
    :Output:
        data unchanged
    """
    end = '\r' if rewrite else '\n'
    def _f(d):
        print(f'{prefix} {d}', end=end)
        return d
    return _f


import logging

def log(logger="snap", fmt="{}"):
    theLogger = logging.getLogger(logger)
    def _f(data):
        theLogger.info(fmt.format(data))
        return data
    return _f



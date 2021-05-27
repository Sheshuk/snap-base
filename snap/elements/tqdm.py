"""
Steps for real-time display
=============================

Wrappers of the `tqdm <https://github.com/tqdm/tqdm>`_ progress-bar to show the iterations count or data values

"""
from tqdm.asyncio import tqdm

def counter(**kwargs):
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
    kwargs.setdefault('bar_format','{desc}[{n: 6.4f}]|{bar}|{r_bar}')
    t = tqdm(**kwargs)
    def _f(d):
        t.n = d
        t.update(0)
        t.refresh()
        return d
    return _f



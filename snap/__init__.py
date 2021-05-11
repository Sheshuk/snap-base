try:
    from .chain import chain
    from .parallel import Parallel
    from . import config
finally:
    __version__ = '1.1.1'

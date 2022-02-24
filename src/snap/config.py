from collections import abc
import logging
logger = logging.getLogger(__name__)

import os
import asyncio
from .chain import chain

def parse_env_vars(s):
    return os.path.expandvars(s)

def read_yaml(fname):
    import yaml
    with open(fname) as f:
        s = parse_env_vars(f.read())
        cfg = yaml.load(s, Loader=yaml.Loader)
    if 'logging' in cfg:
        import logging.config
        logging.config.dictConfig(cfg['logging'])
    return cfg




root_package = 'snap.elements'

class ConfigError(Exception):
    def __init__(self,msg, where):
        super().__init__(f'{msg} in {where}')

def find_module(name):
        if name in globals():
            return globals().get(name)
        else:
            import importlib
            return importlib.import_module(name, root_package)


def find_obj(name):
    if name in globals():
        return globals().get(name)
    else:
        if '.' in name:
            modname,vname = name.rsplit('.',1)
            module = find_module(modname)
            return getattr(module, vname)
        else: 
            raise KeyError(f"Object {name} not found")


obj_label = "obj@"

def build_object(cfg):
    if len(cfg)!=1:
        raise ValueError(f'Object config keys {list(cfg.keys())} !=1')
    for key,args in cfg.items():
        obj = parse(key) 
        return obj(**args)

def parse(cfg):
    try:
        if isinstance(cfg, str):
            if(cfg.startswith(obj_label)):
                res = find_obj(cfg[len(obj_label):])
            else:
                res = cfg
        elif isinstance(cfg, abc.Sequence):
            res = [parse(c) for c in cfg]
        elif isinstance(cfg, abc.Mapping):
            res = {key: parse(val) for key,val in cfg.items()}
            if any([key.startswith(obj_label) for key in res]):
                res = build_object(res)
        else:
            res = cfg

        if(res!=cfg):
            logger.debug(f'parse: {cfg} = {res}')
    except Exception as e:
        raise ConfigError('Configuration error',cfg) from e
    return res

def build_chain(steps=[], source=None, to=[], name='unnamed'):
    "create a chain from config"
    def _force_obj(s):
        "make 's' to start with obj_label"
        def _add_obj(s):
            if s.startswith(obj_label):
                return s
            else:
                return obj_label+s

        if isinstance(s,str):
            return _add_obj(s)
        elif isinstance(s,abc.Mapping):
            return {_add_obj(key): val for key,val in s.items()}
        else:
            return s
    
    #all steps and sources must be objects
    source=  _force_obj(source)
    steps = [_force_obj(s) for s in steps]
    try:
        logger.debug(f'Building chain "{name}"')
        return chain(*parse(steps), source=parse(source), targets=parse(to), name=name)
    except Exception as e:
        raise ConfigError(f'Error building chain "{name}"','node') from e


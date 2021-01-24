from collections import abc
import logging
logger = logging.getLogger(__name__)

import asyncio
from .chain import chain

def read_yaml(fname):
    import yaml
    with open(fname) as s:
        cfg = yaml.load(s, Loader=yaml.Loader)
    if 'logging' in cfg:
        import logging.config
        logging.config.dictConfig(cfg['logging'])
    return cfg




root_package = 'snap'

def find_module(name):
        logger.debug(f'search for Module {name}')
        if name in globals():
            logger.debug('found in globals')
            return globals().get(name)
        else:
            logger.debug(f'trying to import {name} from sys.')
            import importlib
            return importlib.import_module(name, root_package)


def find_obj(name):
    logger.debug(f'search for Object {name}')
    
    if name in globals():
        logger.debug('found in globals')
        return globals().get(name)
    else:
        if '.' in name:
            modname,vname = name.rsplit('.',1)
            logger.debug(f'split to {modname}, {vname}')
            module = find_module(modname)
            logger.debug(f'Found module {module}')
            return getattr(module, vname)
        else: 
            raise KeyError(f"Object {name} not found")


obj_label = "obj@"

def build_object(cfg):
    logger.info(f'Build object from {cfg}')
    if len(cfg)!=1:
        raise ValueError(f'Object config keys {list(cfg.keys())} !=1')
    for key,args in cfg.items():
        obj = parse(key) 
        return obj(**args)

def parse(cfg):
    if isinstance(cfg, str):
        logger.info(f'Parse str {cfg}')
        if(cfg.startswith(obj_label)):
            res = find_obj(cfg[len(obj_label):])
        else:
            res = cfg
    elif isinstance(cfg, abc.Sequence):
        logger.info(f'Parse collection: {cfg}')
        res = [parse(c) for c in cfg]
    elif isinstance(cfg, abc.Mapping):
        logger.info(f'Parse dict: {cfg}')
        res = {key: parse(val) for key,val in cfg.items()}
        if any([key.startswith(obj_label) for key in res]):
            res = build_object(res)
    else:
        logger.info(f'Parse other {cfg}')
        res = cfg
    logger.info(f'res = {res}')
    return res

def build_chain(steps=[], source=None, to=[]):
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
     
    return chain(*parse(steps), source=parse(source), targets=parse(to))


def build_node(config):
    """
    create node from the configuration
    
    parameters:
    * config - a dict of chain configurations.
            Each chain configuration is a dict containing:
                * steps (iterable): list with processing steps (async gen func/buffer object/)
                * source (async generator, optional): where the data appears
                * to (list of str, optional): names of chains, where the output is forwarded
            If a chain has no source, it should be receiving data from another chain (its key should be listed in targets)
            If a chain has no targets (to), the data is not forwarded (i.e. end of a pipeline)

    returns: 
        list of asyncio tasks, to be run with `asyncio.gather`.
    """

    #create input queues for chains without sources
    for name,chain_cfg in config.items():
        if chain_cfg.get('source',None) is None:
            chain_cfg['source'] = asyncio.Queue()

    for name,chain_cfg in config.items():
        #link targets to input queues
        tgts = chain_cfg.get('to',[])
        if isinstance(tgts, str):
            tgts=[tgts]
        chain_cfg['to'] = [config[t]['source'] for t in tgts]

    #create chains
    tasks = [build_chain(**cfg) for cfg in config.values()]
    return tasks

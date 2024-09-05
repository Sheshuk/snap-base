from importlib import import_module
import os, sys
import yaml

from dataclasses import dataclass

_root_package = 'snap.elements'

# get current path and add it for the modules import
current_dir = os.path.abspath(os.getcwd())
sys.path.append(current_dir)


def find_python_module(name, do_import=False):
    try:
        return sys.modules[name]
    except KeyError:
        return import_module(name, _root_package)

def find_python_obj(name):
    try:
        return globals()[name]
    except KeyError:
        if '.' in name:
            modname,vname = name.rsplit('.',1)
            module = find_python_module(modname, do_import=True)
            return getattr(module, vname)
        else: 
            raise 

def build_python_obj(name, args):
    obj = find_python_obj(name)
    try:
        instance = obj(**args)
        return instance
    except Exception as e:
        raise RuntimeError(f"Failed to build object '{name}' of type '{type(obj)}'") from e


class SourceCfg(str): 
    def __init__(self, s):
        if '.' not in s:
            s='.io.recv'
    
class ElementCfg:
    def __init__(self, name, cfg=None):
        self.name = name
        self.cfg = cfg
        self.mark = None
        self.is_source = isinstance(self.name, SourceCfg)
    
    def build(self):
        try:
            if self.cfg is None:
                return find_python_obj(self.name)
            else: 
                return build_python_obj(self.name, self.cfg)
        except Exception as e:
            raise yaml.constructor.ConstructorError(None,None, 
            problem=f'Failed to build element {self}',
            problem_mark=self.mark) from e

    def __repr__(self):
        s = f'<{"S" if self.is_source else ""} name={repr(self.name)} ({self.cfg})>'
        return s

    @classmethod
    def from_dict(cls, d):
        try:
            name,cfg = list(d.items())[0]
        except AttributeError:
            name,cfg = d, None
        return cls(name, cfg)

@dataclass
class ChainCfg:
    name: str
    source: ElementCfg|None
    elements: list[ElementCfg]
    
    def build(self):
        source = self.source.build() if self.source else None
        elements = [e.build() for e in self.elements]
        return ChainCfg(self.name, source, elements)

@dataclass
class NodeCfg:
    name: str
    chains: list[ChainCfg]

def construct_node(loader, name, data):
    name = name.split(':',1)[-1]
    chains = loader.construct_sequence(data)
    return NodeCfg(name=name, chains=chains)

def construct_chain(loader, name, data):
    #construct basic elements
    steps = loader.construct_sequence(data, deep=True)
    elements = [ElementCfg.from_dict(s) for s in steps]
    name = name.split(':',1)[-1]
    #store node pointers in elements
    for e,s in zip(elements,data.value):
        e.mark = s.start_mark
    #grab the first element as source
    if elements[0].is_source:
        source = elements.pop(0)
    else:
        source = None
    #check than no other elements are marked as source
    for e in elements:
        if e.is_source:
            raise yaml.constructor.ConstructorError(
                problem='Only the first chain element can be used as source!',
                problem_mark=e.mark)
    return ChainCfg(name, source, elements)

def construct_from(loader, data):
    name = loader.construct_scalar(data)
    if '.' in name:
        return SourceCfg(name)
    else:
        return {SourceCfg('.io.recv'):{'address':name}}

def construct_to(loader, data):
    if isinstance(data, yaml.SequenceNode):
        tgt = loader.construct_sequence(data)
    else:
        tgt = [loader.construct_scalar(data)]
    return {'.io.send':{'address': tgt}}

def construct_object(loader, name, data):
    name = name.split(':',1)[-1]
    print(f'cpnstruct_object from {name}, {data}')
    cfg = loader.construct_mapping(data)
    print(f'cfg={cfg}')
    if cfg is None:
        return find_python_obj(name)
    else: 
        return build_python_obj(name, cfg)

loader = yaml.Loader
loader.add_multi_constructor(u'!Node', construct_node)
loader.add_multi_constructor(u'!chain', construct_chain)
loader.add_constructor(u'!from', construct_from)
loader.add_constructor(u'!to', construct_to)
loader.add_multi_constructor(u'!obj', construct_object)

def parse_env_vars(s):
    return os.path.expandvars(s)

def read_yaml(fname):
    import yaml
    with open(fname) as f:
        s = parse_env_vars(f.read())
        cfg = yaml.load(s, Loader=loader)
    return cfg


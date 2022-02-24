#!/bin/env python3

import logging

logger = logging.getLogger(__name__)

from snap.config import read_yaml, build_chain, ConfigError
from snap.status import status_server

import asyncio
import argparse

import os, sys
import signal

from functools import partial

# get current path and add it for the modules import
current_dir = os.path.abspath(os.getcwd())
sys.path.append(current_dir)

class Node:
    def __init__(self, config:dict):
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
        self.tasks = {name:build_chain(**chain_cfg, name=name) for name,chain_cfg in config.items()}
        logger.debug(f"Constructed node: {self.tasks}")

    def add_status_server(self, address):
        self.tasks['status_check']=status_server(address=status, status=b'OK')

    def cancel(self):
        logger.info("Cancelling tasks!")
        for t in self.running_tasks:
            logger.debug(f'Cancel task{t}')
            t.cancel()

    async def run(self):
        self.running_tasks = [asyncio.create_task(self.tasks[n],name=n) for n in tasks]
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGTERM,self.cancel)
        loop.add_signal_handler(signal.SIGINT,self.cancel)
        try:
            await asyncio.gather(*self.running_tasks, return_exceptions=False)
        except asyncio.CancelledError:
            logger.info("Cancelled")
        finally:
            logger.info("Finished")

    @classmethod
    def from_yaml(cls, filename, nodename='node'):
        cfg = read_yaml(filename)
        try: 
            node = cls(cfg[nodename])
        except ConfigError as e:
            logger.error(e)
            raise
        except KeyError as e:
            all_nodes = list(cfg.keys())
            msg = f'No node="{nodename}" in config "{filename}".'+ \
            f'Available nodes are: {all_nodes}'
            logger.error(msg)
            raise KeyError(msg)

parser= argparse.ArgumentParser(description='SuperNova Async Pipeline: run a given NODE from config')
parser.add_argument('config',
        help='Nodes configuration file in yaml format')
parser.add_argument('-n','--node',metavar='NAME',default='node',
        help='Node name (default="node")')
parser.add_argument('-S','--status',metavar='ADDRESS',default=None,
        help='ZMQ socket address, where the reply server for status checks will bind. Default: no status server.')
parser.add_argument('-v','--verbose', metavar='LOG_LEVEL', choices=['CRITICAL','ERROR','WARNING','INFO','DEBUG'],
        help='Override the log level')

def run():
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=args.verbose)
    node = Node.from_yaml(args.config, args.node)
    if args.status:
        node.add_status_server(args.status)
    asyncio.run(node.run())

if __name__=='__main__':
    run()

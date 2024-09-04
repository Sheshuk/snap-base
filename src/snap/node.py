#!/bin/env python3

import logging

logger = logging.getLogger(__name__)

from snap.config import read_yaml, NodeCfg
from snap.status import status_server
from snap.chain import make_chains

import asyncio
import argparse

import os, sys
import signal

from functools import partial

class Node:
    def __init__(self, name, chains):
        """
        create node from the configuration
        
        parameters:
            chains
       """
        #create chains
        self.chains = chains
        self.running_tasks = None
        logger.debug(f"Constructed node: {self.chains}")

    def add_status_server(self, address):
        self.tasks['status_check']=status_server(address=status, status=b'OK')

    def cancel(self):
        logger.info("Cancelling tasks!")
        for t in self.running_tasks:
            logger.debug(f'Cancel task{t}')
            t.cancel()

    async def run(self):
        self.running_tasks = [asyncio.create_task(c.run(),name=c.name) for c in self.chains]
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
            node_cfg = cfg[nodename]
        except KeyError as e:
            all_nodes = list(cfg.keys())
            msg = f'No node="{nodename}" in config "{filename}".'+ \
            f'Available nodes are: {all_nodes}'
            logger.error(msg)
            raise KeyError(msg)
        return cls.from_cfg(node_cfg)

    @classmethod
    def from_cfg(cls, node_cfg:NodeCfg):
        #instantiate the python objects
        chains_built = [c.build() for c in node_cfg.chains]
        #subdivide the chains if needed
        chains = [make_chains(c.elements, c.source, c.name) for c in chains_built]
        chains = [c for ch in chains for c in ch]
        #create the node
        return cls(name=node_cfg.name, chains=chains)

def get_parser():
    parser= argparse.ArgumentParser(description='SuperNova Async Pipeline: run a given NODE from config')
    parser.add_argument('config',
            help='Nodes configuration file in yaml format')
    parser.add_argument('-n','--node',metavar='NAME',default='node',
            help='Node name (default="node")')
    parser.add_argument('-S','--status',metavar='ADDRESS',default=None,
            help='ZMQ socket address, where the reply server for status checks will bind. Default: no status server.')
    parser.add_argument('-v','--verbose', metavar='LOG_LEVEL', choices=['CRITICAL','ERROR','WARNING','INFO','DEBUG'],
            help='Override the log level')
    return parser

def run():

    args = get_parser().parse_args()
    if args.verbose:
        logging.basicConfig(level=args.verbose)
    node = Node.from_yaml(args.config, args.node)

    if args.status:
        node.add_status_server(args.status)
    asyncio.run(node.run())

#if __name__=='__main__':
#    run()

#!/usr/bin/env python

from distutils.core import setup

setup(name='snap-base',
        version='0.1',
        description='SuperNova Async Pipeline base package',
        author='Andrey Sheshukov',
        author_email='ash@jinr.ru',
        licence='GNU GPLv3',
        packages=['snap'],
        scripts=['scripts/snap'],
        install_requires=['pyzmq>=20','pyyaml>=3.5']
     )


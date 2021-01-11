#!/usr/bin/env python

from distutils.core import setup
with open('README.md') as f:
    readme = f.read()

setup(name='snap-base',
        version='1.0.0',
        description='SuperNova Async Pipeline: base package',
        long_description=readme,
        long_description_content_type='text/markdown',
        url='https://github.com/Sheshuk/snap-base',
        author='Andrey Sheshukov',
        author_email='ash@jinr.ru',
        licence='GNU GPLv3',
        packages=['snap'],
        scripts=['scripts/snap'],
        install_requires=['pyzmq>=20','pyyaml>=3.5']
     )


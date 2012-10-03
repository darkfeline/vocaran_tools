#!/usr/bin/env python3

from distutils.core import setup
import os
import os.path
import re


def get_resources(dir):
    l = []
    rget_resources(dir, l)
    return l


def make_listing(dir):
    return (dir, [os.path.join(dir, x) for x in os.listdir(dir) if
        os.path.isfile(os.path.join(dir, x))])


def rget_resources(dir, l):
    l.append(make_listing(dir))
    for d in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, d)):
            rget_resources(os.path.join(dir, d), l)


def get_modules(dir):
    p_py = re.compile(r'(.+)\.py')
    return [p_py.match(x).group(1) for x in os.listdir(dir) if p_py.match(x)]


def get_packages(dir):
    l = []
    rget_packages(dir, '', l)
    return l


def rget_packages(start, dir, l):
    ls = os.listdir(os.path.join(start, dir))
    if '__init__.py' in ls:
        l.append(dir.replace('/', '.'))
    for x in [x for x in ls if os.path.isdir(os.path.join(start, dir, x))]:
        rget_packages(start, os.path.join(dir, x), l)

setup(
    name='vocaran_tools',
    version='2.0',
    description='Vocaloid song dl tools',
    author='Allen Li',
    author_email='darkfeline@abagofapples.com',
    package_dir={'': 'src'},
    py_modules=get_modules('src'),
    packages=get_packages('src'),
    scripts=['vct']
)

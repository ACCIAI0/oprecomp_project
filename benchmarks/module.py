#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pathlib

from benchmarks.benchmark import Benchmark


__available = {
    el.name: el for el in
    [Benchmark(x.stem) for x in pathlib.Path.cwd().glob(Benchmark.b_home + '*')
     if x.is_dir() and not x.stem.startswith('.')]
}


def get_all_names():
    return __available.keys()


def exists(name: str) -> bool:
    """
    Checks if a benchmark with the given name exists.
    :param name: the name of the benchmark to check the existence of.
    :return: True if the benchmark with the given name exists, False otherwise.
    """
    return name in __available.keys()


def get_benchmark(name: str) -> Benchmark:
    """
    Returns a Benchmark object having the given name.
    :param name: The name of the Benchmark.
    :return: a Benchmark object relative to the given benchmark name, None if it doesn't exist.
    """
    return __available.get(name, None)
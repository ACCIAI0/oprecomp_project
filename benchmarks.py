#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import pathlib
import json

import vargraph
from utils import io_utils


class Benchmark:
    b_home = 'flexfloat-benchmarks/'

    def __init__(self, name):
        self.__name = name
        self.__lazyEval = False
        self.__graph = None
        self.__nVars = -1
        self.__home = Benchmark.b_home + name + "/"
        self.__configs = self.__home + "config_file.txt"

        with open(self.__home + "global_info.json") as jfile:
            jdict = json.load(jfile)
        self.__map = jdict.get('map', None)
        self.__flag = jdict.get('flag', False)

    def __evaluate(self):
        if not self.__lazyEval:
            self.__graph = vargraph.parse_vars_file(self.__home + "program_vardeps.json")
            self.__nVars = len(self.__graph)
            self.__lazyEval = True

    @property
    def name(self) -> str:
        return self.__name

    @property
    def graph(self):
        self.__evaluate()
        return self.__graph

    @property
    def vars_number(self) -> int:
        self.__evaluate()
        return self.__nVars

    @property
    def home(self):
        return self.__home

    @property
    def map(self):
        return self.__map

    @property
    def configs_file(self):
        return self.__configs

    @property
    def is_flagged(self):
        return self.__flag

    def plot_var_graph(self):
        vargraph.plot(self.graph)

    def get_binary_relations(self) -> dict:
        return {
            'leq': vargraph.extract_leq_relations(self.graph),
            'cast': vargraph.extract_cast_to_temp_relations(self.graph)
        }


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


def __check_output(floating_result, target_result):
    very_large_error = 1000
    if len(floating_result) != len(target_result) or \
            all(v == 0 for v in floating_result) != all(v == 0 for v in target_result):
        return very_large_error

    sqnr = 0.00
    for i in range(len(floating_result)):
        # if floating_result[i] == 0, check_output returns 1: this is an
        # unwanted behaviour
        if floating_result[i] == 0.00:
            continue    # mmmhhh, TODO: fix this in a smarter way

        # if there is even just one inf in the result list, we assume that
        # for the given configuration the program did not run properly
        if str(floating_result[i]) == 'inf':
            return float('nan')

        signal_sqr = target_result[i] ** 2
        error_sqr = (floating_result[i] - target_result[i]) ** 2
        temp = 0.00
        if error_sqr != 0.00:
            temp = signal_sqr / error_sqr
            temp = 1.0 / temp
        if temp > sqnr:
            sqnr = temp

    return sqnr


def __run_check(program, bm: Benchmark, target_result, dataset_index):
    params = [program, bm.name, bm.map, '42']
    if -1 != dataset_index:
        params.append(str(dataset_index))
    output = subprocess.Popen(params, stdout=subprocess.PIPE).communicate()[0]
    result = io_utils.parse_output(output.decode('utf-8'))
    return __check_output(result, target_result)


def run_benchmark_with_config(bm: Benchmark, opt_config, args):
    """
    Runs a Benchmark with a given bit numbers configuration and returns the actual error such a configuration creates.
    :param args: arguments passed at the start of the program. It's a needed parameter because there is cross-reference.
    :param bm: the benchmark to run.
    :param opt_config: the configuration of bit numbers to use in the run.
    :return: the actual error given the configuration.
    """

    io_utils.write_configs_file(bm.configs_file, opt_config)
    program = Benchmark.b_home + 'multiDataSet.sh'
    target_file = bm.home + 'target.txt'
    if -1 != args.dataset_index:
        target_file = bm.home + 'targets/target_{}.txt'.format(args.dataset_index)

    target_result = io_utils.read_target(target_file)
    error = __run_check(program, bm, target_result, args.dataset_index)

    io_utils.write_configs_file(bm.configs_file, [args.max_bits_number] * bm.vars_number)
    return error

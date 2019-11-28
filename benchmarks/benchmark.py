#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from benchmarks import vargraph


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
        return self.__flag or self.__nVars > 20

    def print_var_graph(self, img_name):
        vargraph.save(self.graph, img_name)

    def get_binary_relations(self) -> dict:
        return {r.name: r for r in
                [
                    vargraph.extract_leq_relations(self.graph),
                    vargraph.extract_cast_to_temp_relations(self.graph)
                ]
                }

    def check_binary_relations_for(self, config) -> bool:
        return all([br.check_config(config) for br in self.get_binary_relations().values()])

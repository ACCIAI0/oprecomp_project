#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from optimization import iteration as it
from argsmanaging import args


class Log:
    def __init__(self, struct=None):
        if not struct:
            self.__benchmark = args.benchmark
            self.__target = args.error
            self.__changeProbability = args.variable_change_probability
            self.__dataset = args.dataset_index
            self.__iterations = []
            self.__neighbourSearches = []
            self.__best = None
            self.__time = None
        else:
            self.__benchmark = struct['benchmark']
            self.__target = struct['target']
            self.__changeProbability = struct['changeProbability']
            self.__dataset = struct['dataset']
            self.__iterations = struct['iterations']
            self.__neighbourSearches = struct['neighbourSearches']
            self.__best = struct['best']
            self.__time = struct['time']

    def __str__(self):
        return json.dumps(self.__dict__, default=lambda o: str(o) if not hasattr(o, '__dict__') else o.__dict__, indent=4)\
            .replace('_Log__', '')

    @property
    def benchmark(self):
        return self.__benchmark

    @property
    def target(self):
        return self.__target

    @property
    def iterations(self):
        return self.__iterations.copy()

    @property
    def change_probability(self):
        return self.__changeProbability

    @property
    def dataset_index(self):
        return self.__dataset

    @property
    def neighbour_searches(self):
        return self.__neighbourSearches

    @property
    def best_solution(self):
        return self.__best

    @property
    def time(self):
        return self.__time

    @time.setter
    def time(self, t):
        self.__time = t

    @best_solution.setter
    def best_solution(self, b):
        self.__best = b

    def insert_iteration(self, iteration: it.Iteration, r_stats, c_stats):
        self.__iterations.append({
            'configuration': iteration.config,
            'exp': iteration.get_error_log(),
            'error': iteration.get_error(),
            'p_exp': iteration.get_predicted_error_log(),
            'generated': iteration.has_failed,
            'mae': float(r_stats['MAE']),
            'mse': float(r_stats['MSE']),
            'rmse': float(r_stats['RMSE']),
            'mape': float(r_stats['MAPE']),
            'precision': c_stats['precision'],
            'recall': c_stats['recall'],
            'fscore': c_stats['fscore'],
            'accuracy': c_stats['accuracy']
        })

    def insert_neighbour_search(self, n_possible_solutions, config):
        self.__neighbourSearches.append({
            'n_possibilities': n_possible_solutions,
            'config': config
        })

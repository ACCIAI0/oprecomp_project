#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import float_info

import numpy

from argsmanaging import args


class IterationIterator:
    def __init__(self, it):
        self.__it = it

    def __next__(self):
        if self.__it is None:
            raise StopIteration
        r = self.__it
        self.__it = self.__it.previous_iteration
        return r


class Iteration:
    def __init__(self, config, error, predicted_error, predicted_class, previous_iteration, failed):
        self.__config = config
        self.__error = error
        self.__pError = predicted_error
        self.__pClass = predicted_class
        self.__previous = previous_iteration
        self.__failed = failed

        if self.__previous is None:
            self.__iterN = 1
            self.__p_best_cfg = None
            self.__p_best_err = 0
        else:
            self.__iterN = self.__previous.iter_n + 1
            self.__p_best_cfg, self.__p_best_err = self.__previous.best_config_and_error

    def __str__(self):
        return str(self.__config) + \
               " --> " + \
               "{:.3f}".format(self.get_error_log()) + \
               " | " + \
               "{:.3f}".format(self.get_predicted_error_log()) + \
               " (" + str(self.__pClass) + ")"

    def __iter__(self):
        return IterationIterator(self)

    @property
    def iter_n(self):
        return self.__iterN

    @property
    def previous_iteration(self):
        return self.__previous

    @property
    def config(self):
        return self.__config

    def get_error(self):
        return self.__error

    def get_error_class(self):
        return int(self.__error >= args.large_error_threshold)

    def get_error_log(self):
        return -numpy.log10(self.__error) if 0 != self.__error else float_info.min

    def get_predicted_error_log(self):
        return self.__pError

    def get_predicted_class(self):
        return self.__pClass

    @property
    def is_feasible(self):
        return self.get_error_log() >= -numpy.log10(args.error)

    def get_delta_config(self):
        if self.__previous is None:
            return [0] * len(self.__config)
        return [i - j for i, j in zip(self.__previous.get_config(), self.__config)]

    def get_delta_error(self):
        if self.__previous is None:
            return 0
        return self.__previous.get_error() - self.__error

    @property
    def best_config_and_error(self):
        res = None
        res_err = 0

        if self.__p_best_cfg is None:
            if self.is_feasible and not self.__failed:
                res, res_err = self.__config, self.__error
        else:
            sum_c = sum(self.__config)
            sum_c_p = sum(self.__p_best_cfg)

            if self.is_feasible and (sum_c < sum_c_p or (sum_c == sum_c_p and self.__error < self.__p_best_err)):
                res, res_err = self.__config, self.__error
            else:
                res, res_err = self.__p_best_cfg, self.__p_best_err

        return res, res_err

    @property
    def has_failed(self):
        return self.__failed

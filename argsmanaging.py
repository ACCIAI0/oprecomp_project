#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum

import numpy

import benchmarks
import utils


class ArgsError(Enum):
    NO_ERROR = 0
    UNKNOWN_BENCHMARK = 1
    INT_CAST_ERROR = 2
    INT_INVALID_VALUE = 3
    REGRESSOR_ERROR = 4
    CLASSIFIER_ERROR = 5
    FLOAT_CAST_ERROR = 6
    FLOAT_INVALID_VALUE = 7
    VALUE_OUT_OF_BOUNDS = 8


class Regressor(Enum):
    NEURAL_NETWORK = 'NN'


class Classifier(Enum):
    DECISION_TREE = 'DT'


class ArgumentsHolder:

    def __init__(self):
        self.__benchmark = None
        self.__exp = 0
        self.__regressor = Regressor.NEURAL_NETWORK
        self.__classifier = Classifier.DECISION_TREE
        self.__datasetIndex = 0
        self.__minBitsNumber = 4
        self.__maxBitsNumber = 53
        self.__largeErrorThreshold = .9
        self.__probability = .3

    @property
    def benchmark(self):
        return self.__benchmark
    
    @benchmark.setter
    def benchmark(self, bm):
        self.__benchmark = bm

    @property
    def exponent(self):
        return self.__exp

    @property
    def error(self):
        return numpy.float_power(10, -self.__exp)

    @exponent.setter
    def exponent(self, exp):
        self.__exp = exp

    @property
    def regressor_type(self):
        return self.__regressor

    @regressor_type.setter
    def regressor_type(self, regressor):
        self.__regressor = regressor

    @property
    def classifier_type(self):
        return self.__classifier

    @classifier_type.setter
    def classifier_type(self, classifier):
        self.__classifier = classifier

    @property
    def dataset_index(self):
        return self.__datasetIndex

    @dataset_index.setter
    def dataset_index(self, index):
        self.__datasetIndex = index

    @property
    def min_bits_number(self):
        return self.__minBitsNumber

    def set_min_bits_number(self, min_bits):
        self.__minBitsNumber = min_bits

    @property
    def max_bits_number(self):
        return self.__maxBitsNumber

    @max_bits_number.setter
    def max_bits_number(self, max_bits):
        self.__maxBitsNumber = max_bits

    @property
    def large_error_threshold(self):
        return self.__largeErrorThreshold

    @large_error_threshold.setter
    def large_error_threshold(self, large_error_threshold):
        self.__largeErrorThreshold = large_error_threshold

    @property
    def variable_change_probability(self):
        return self.__probability

    @variable_change_probability.setter
    def variable_change_probability(self, probability):
        self.__probability = probability

    @property
    def is_legal(self):
        return self.__benchmark is not None and self.__exp != 0

    def __str__(self):
        return "Benchmark $blue#{}$ ($blue#{:.1e}$, vars in $blue#{}$). $blue#{}$ regressor and $blue#{}$ classifier"\
            .format(self.__benchmark, self.error,
                    "[{:d}, {:d}]".format(self.__minBitsNumber, self.__maxBitsNumber), self.__regressor.name,
                    self.__classifier.name)
    
    
args = ArgumentsHolder()


def __int_value(value):
    error = ArgsError.NO_ERROR
    v = 0
    try:
        v = int(value)
        if 0 >= v:
            error = ArgsError.INT_INVALID_VALUE
    except ValueError:
        error = ArgsError.INT_CAST_ERROR
    return error, v


def __float_value(value):
    error = ArgsError.NO_ERROR
    v = 0
    try:
        v = float(value)
        if 0 >= v:
            error = ArgsError.FLOAT_INVALID_VALUE
    except ValueError:
        error = ArgsError.FLOAT_CAST_ERROR
    return error, v


def __benchmark(value):
    error = ArgsError.NO_ERROR
    if not benchmarks.exists(value):
        error = ArgsError.UNKNOWN_BENCHMARK
    if ArgsError.NO_ERROR == error:
        args.benchmark = value
    return error, value


def __exp(value):
    error, v = __int_value(value)
    if ArgsError.NO_ERROR == error:
        args.exponent = v
    return error, args.error


def __regressor(value):
    error = ArgsError.NO_ERROR
    if value not in [reg.value for reg in Regressor]:
        error = ArgsError.REGRESSOR_ERROR
    if ArgsError.NO_ERROR == error:
        args.regressor_type = Regressor(value)
    return error, value


def __classifier(value):
    error = ArgsError.NO_ERROR
    if value not in [cl.value for cl in Classifier]:
        error = ArgsError.CLASSIFIER_ERROR
    if ArgsError.NO_ERROR == error:
        args.classifier_type = Classifier(value)
    return error, value


def __dataset(value):
    error, v = __int_value(value)
    if ArgsError.NO_ERROR == error:
        args.dataset_index = v
    return error, v


def __min_bits(value):
    error, v = __int_value(value)
    if ArgsError.NO_ERROR == error:
        args.set_min_bits_number(v)
    return error, v


def __max_bits(value):
    error, v = __int_value(value)
    if ArgsError.NO_ERROR == error:
        args.max_bits_number = v
    return error, v


def __large_error_threshold(value):
    error, v = __float_value(value)
    if ArgsError.NO_ERROR == error:
        args.large_error_threshold = v
    return error, v


def __probability(value):
    error, v = __float_value(value)
    if 0 > v or 1 < v:
        error = ArgsError.VALUE_OUT_OF_BOUNDS
    if ArgsError.NO_ERROR == error:
        args.variable_change_probability = v
    return error, v


def error_handler(e, param, value):
    assert isinstance(param, str)
    param = param.replace('-', '')
    err_str = "There was an input error"
    if ArgsError.UNKNOWN_BENCHMARK == e:
        err_str = "Can't find a benchmark called {}".format(value)
    elif ArgsError.INT_CAST_ERROR == e:
        err_str = "Expected an integer value, found '{}' as {}".format(value, param)
    elif ArgsError.INT_INVALID_VALUE == e:
        err_str = "{} value must be greater than 0".format(param)
    elif ArgsError.REGRESSOR_ERROR == e:
        s = ''
        for reg in Regressor:
            s += reg.value + ', '
        s = s[:len(s) - 2]
        err_str = "Invalid regressor {}. Possible values are: {}".format(value, s)
    elif ArgsError.CLASSIFIER_ERROR == e:
        s = ''
        for cl in Classifier:
            s += cl.value + ', '
        s = s[:len(s) - 2]
        err_str = "Invalid classifier {}. Possible values are: {}".format(value, s)

    if ArgsError.NO_ERROR is not e:
        utils.print_n("$b#red#" + err_str + "$")
        exit(e.value)


__args = {
    '-bm': __benchmark,
    '-exp': __exp,
    '-reg': __regressor,
    '-cfr': __classifier,
    '-ds': __dataset,
    '-b': __min_bits,
    '-B': __max_bits,
    '-et': __large_error_threshold,
    '-p': __probability
}


def handle_args(argv):
    """
        Handles the arguments passed as parameters at the start of the program. It can cause the entire program to quit
        if any error is encountered (see ArgsError for the possible error types).
        :param argv: arguments array. from the starting script, it is the system arguments list slice from the second
        argument onward.
        :return: an ArgumentHolder if all arguments are legal. If any of them is not, the program quits.
    """

    if 0 == len(argv):
        print("Some parameters are mandatory. Use -help to see all possible parameter names.")
        exit(-1)

    if argv[0] == '-help':
        s = ''
        for a in __args.keys():
            s += a + ', '
        s = s[:len(s) - 2]
        print("Possible parameters: {}".format(s))
        exit(0)

    for i in range(0, len(argv) - 1, 2):
        p = argv[i]
        v = None

        if not p.startswith('-'):
            print("Invalid parameter name {}".format(p))
            exit(1)

        if i + 1 < len(argv):
            v = argv[i + 1]
        error, value = __args[p](v)
        error_handler(error, p, v)
    if not args.is_legal:
        utils.print_n("$b#red#Benchmark and error exponent are mandatory$")
        exit(1)
    return args
    


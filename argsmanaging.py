#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum

import numpy

import benchmarks
import utils


class Regressor(Enum):
    NEURAL_NETWORK = 'NN'


class Classifier(Enum):
    DECISION_TREE = 'DT'


class ArgError(Enum):
    NO_ERROR = 0
    CONVERSION_ERROR = 1
    UNKNOWN_VALUE = 2
    INVALID_VALUE = 3
    MISSING_PARAMETER = 4
    UNKNOWN_ARGUMENT = 5


class ArgChecker:
    def __init__(self, code: str, p_num: int, default, description: str,
                 converter=str, checks=(lambda _: ArgError.NO_ERROR)):
        self.__code = code
        self.__pNum = p_num
        self.__default = default
        self.__description = description
        self.__converter = converter
        self.__checks = checks
        self.__last_value = default

    @property
    def code(self):
        return self.__code

    @property
    def description(self):
        res = self.__description
        is_float = isinstance(self.__default, float)
        if self.__default is not None and (is_float and not numpy.isnan(self.__default) or not is_float):
            res += "\n\t\tDEFAULT = " + str(self.__default)
        return res

    @property
    def p_num(self):
        return self.__pNum

    @property
    def last_value(self):
        return self.__last_value

    def handle(self, argv: list):
        if self.p_num > len(argv):
            return ArgError.MISSING_PARAMETER, None
        if 0 == self.p_num:
            self.__last_value = True
            return ArgError.NO_ERROR, argv

        value = argv[0]
        if 1 < self.p_num:
            value = argv[:self.p_num]

        try:
            self.__last_value = self.__converter(value)
            return self.__checks(self.__last_value), argv[self.__pNum:]
        except ValueError:
            return ArgError.CONVERSION_ERROR, None


def __check_gt_zero(v):
    return ArgError.NO_ERROR if 0 < v else ArgError.INVALID_VALUE


def __check_ge_zero(v):
    return ArgError.NO_ERROR if 0 <= v else ArgError.INVALID_VALUE


def __gen_interval_check(lb, ub):
    return lambda v: ArgError.NO_ERROR if lb < v <= ub else ArgError.INVALID_VALUE


checkers = {
    '-bm': ArgChecker('bm', 1, None, "[MANDATORY] Specifies the benchmark to use.", str,
                      (lambda v: ArgError.NO_ERROR if benchmarks.exists(v) else ArgError.UNKNOWN_VALUE)),
    '-exp': ArgChecker('exp', 1, float('nan'),
                       "[MANDATORY] Specifies the target error: '-exp n' is considered as the error 1e-n.", int,
                       __check_gt_zero),
    '-reg': ArgChecker('reg', 1, Regressor.NEURAL_NETWORK, "Specifies what type of regressor to use.", Regressor),
    '-cfr': ArgChecker('cfr', 1, Classifier.DECISION_TREE, "Specifies what type of classifier to use.", Classifier),
    '-ds': ArgChecker('ds', 1, 0, "Specifies the dataset index to use for training.", int, __gen_interval_check(0, 29)),
    '-b': ArgChecker('b', 1, 4, "Specifies the minimum number of bits for a variable.", int, __check_gt_zero),
    '-B': ArgChecker('B', 1, 53, "Specifies the maximum number of bits for a variable.", int, __check_gt_zero),
    '-et': ArgChecker('et', 1, .9, "Specifies the threshold over which errors are considered large.",
                      float, __check_gt_zero),
    '-p': ArgChecker('p', 1, .3, "Specifies the probability of changing a bit number when generating neighbours.",
                     float, __gen_interval_check(0, 1)),
    '-pg': ArgChecker('pg', 0, False, "Specifies whether or not to print the variable graph after the run.", bool),
    '-limit': ArgChecker('limit', 1, 0, "Orders of magnitude within which to find the solution, starting from -exp.",
                         int, __check_ge_zero),
    '-manual': ArgChecker('manual', 0, False,
                          "Specifies whether or not to enable manual step by step in looking for solutions.", bool)
}


class ArgumentsHolder:
    def __init__(self):
        pass

    @property
    def benchmark(self):
        return checkers['-bm'].last_value

    @property
    def exponent(self):
        return checkers['-exp'].last_value

    @property
    def error(self):
        return numpy.float_power(10, -self.exponent)

    @property
    def error_log(self):
        return -numpy.log10(self.error)

    @property
    def regressor_type(self):
        return checkers['-reg'].last_value

    @property
    def classifier_type(self):
        return checkers['-cfr'].last_value

    @property
    def dataset_index(self):
        return checkers['-ds'].last_value

    @property
    def min_bits_number(self):
        return checkers['-b'].last_value

    @property
    def max_bits_number(self):
        return checkers['-B'].last_value

    @property
    def large_error_threshold(self):
        return checkers['-et'].last_value

    @property
    def variable_change_probability(self):
        return checkers['-p'].last_value

    @property
    def print_graph(self):
        return checkers['-pg'].last_value

    @property
    def search_limit(self):
        return checkers['-limit'].last_value

    @property
    def manual_toggled(self):
        return checkers['-manual'].last_value

    @property
    def is_legal(self):
        return self.benchmark is not None and \
               not numpy.isnan(self.exponent) and \
               self.min_bits_number < self.max_bits_number

    def __str__(self):
        return "Benchmark $blue#{}$ ($blue#{:.1e}$, vars in $blue#{}$). $blue#{}$ regressor and $blue#{}$ classifier" \
            .format(self.benchmark, self.error, "[{:d}, {:d}]".format(self.min_bits_number, self.max_bits_number),
                    self.regressor_type.name, self.classifier_type.name)


args = ArgumentsHolder()


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
        if 2 <= len(argv) and argv[1] in checkers.keys():
            print('\t\t' + checkers[argv[1]].description)
        else:
            s = ''
            for a in checkers.keys():
                s += a + '\t\t' + checkers[a].description + '\n\n'
            print(s)
        exit(0)

    while 0 != len(argv):
        key = argv[0]
        try:
            e, argv = checkers[key].handle(argv[1:])
        except KeyError:
            e = ArgError.UNKNOWN_ARGUMENT
        if e != ArgError.NO_ERROR:
            utils.print_n("$b#red#Error {} generated by argument {}$", e.name, key)
            exit(e.value)
    return args

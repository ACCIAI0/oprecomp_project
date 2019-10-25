#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas


class ExamplesGenerator:
    def __init__(self, config, inferred, error, interpolated_errors, cls, interpolated_classes, weights):
        self.__config = config
        self.__inferred = inferred
        self.__class = cls
        self.__interpolatedErrs = interpolated_errors
        self.__interpolatedClasses = interpolated_classes
        self.__error = error
        self.__weights = weights

    def __len__(self):
        return len(self.__inferred) + 1

    def __get_regressor_target(self, only_original):
        res = [self.__error]
        if not only_original:
            res += self.__interpolatedErrs
        return pandas.Series(res)

    def __get_classifier_target(self, only_original):
        res = [self.__class]
        if not only_original:
            res += self.__interpolatedClasses
        return pandas.Series(res)

    def build_data_frame(self, regr_label, clfr_label, only_original=False):
        configs = [self.__config]
        if not only_original:
            configs += self.__inferred

        df = pandas.DataFrame.from_dict({'var_{}'.format(i): [configs[j][i] for j in range(len(configs))]
                                         for i in range(len(configs[0]))})
        df[regr_label] = self.__get_regressor_target(only_original)
        df[clfr_label] = self.__get_classifier_target(only_original)

        return df

    def get_weights(self, only_original=False):
        return [self.__weights[0]] if only_original else self.__weights

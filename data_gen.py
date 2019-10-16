#!/usr/bin/env python
# -*- coding: utf-8 -*-

from argsmanaging import args
import benchmarks
import training

import pandas
import numpy
from sklearn import neighbors as skn


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


def __single_value_gen(v, min_b, max_b):
    p = numpy.random.random()
    if p <= args.variable_change_probability:
        v = int(numpy.clip(v + numpy.floor(numpy.random.normal(scale=2)), min_b, max_b))
    return v


def __find_neighbours(bm: benchmarks.Benchmark, solution):
    n = []
    for _ in range(bm.vars_number * int(1 / args.variable_change_probability) * 10):
        neighbour = [__single_value_gen(solution[i], args.min_bits_number, args.max_bits_number)
                     for i in range(len(solution))]
        n.append(neighbour)

    # Remove doubles by ordering them: equal configurations end up being adjacent elements in the list
    n = sorted(n)
    return [n[i] for i in range(len(n)) if i == 0 or n[i] != n[i-1]]


def infer_examples(bm: benchmarks.Benchmark, session: training.TrainingSession, it):
    w = numpy.maximum(1e-6, numpy.abs(it.get_error_log() - numpy.log10(args.error)))

    neighbours = __find_neighbours(bm, it.config)
    neighbours_w = [w * (1 if all([br.check_config(n) for br in bm.get_binary_relations().values()]) else .001)
                    for n in neighbours]

    knn = skn.KNeighborsRegressor(n_neighbors=5, weights='distance')
    knn.fit(session.full_training_data[['var_{}'.format(i) for i in range(bm.vars_number)]],
            session.full_training_data[['err_log', 'class']])
    predictions = knn.predict(numpy.array(neighbours))

    return ExamplesGenerator(it.config, neighbours, it.get_error_log(), [p[0] for p in predictions],
                             it.get_error_class(), [int(round(p[1])) for p in predictions], [w] + neighbours_w)


def ml_refinement(bm: benchmarks.Benchmark, regressor, classifier,
                  session: training.TrainingSession, examples: ExamplesGenerator):
    regr_target_label = 'reg'
    class_target_label = 'cls'

    df = examples.build_data_frame(regr_target_label, class_target_label)

    clfr_training = session.training_set
    clfr_training[regr_target_label] = session.regressor_target.values
    clfr_training[class_target_label] = session.classifier_target.values
    clfr_training = pandas.concat([clfr_training, df])

    test = session.test_set
    test[regr_target_label] = session.regressor_target_test.values
    test[class_target_label] = session.classifier_target_test.values

    weights = numpy.asarray(examples.get_weights())
    single_session = training.TrainingSession(df, test.copy(), regr_target_label, class_target_label)
    trainer = training.RegressorTrainer.create_for(args.regressor_type, single_session)
    trainer.train_regressor(regressor, weights=weights, verbose=False)
    r_stats = trainer.test_regressor(bm, regressor)

    session = training.TrainingSession(clfr_training, test, regr_target_label, class_target_label)
    trainer = training.ClassifierTrainer.create_for(args.classifier_type, session)
    trainer.train_classifier(classifier)
    c_stats = trainer.test_classifier(bm, classifier)

    return session, r_stats, c_stats

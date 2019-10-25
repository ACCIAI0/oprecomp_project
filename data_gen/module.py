#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
import pandas
import itertools

from data_gen.examples_generator import ExamplesGenerator
from data_gen import error_inferring as ei
from argsmanaging import args
import benchmarks
import training


def __single_value_gen(v, min_b, max_b):
    p = numpy.random.random()
    if p <= args.variable_change_probability:
        v = int(numpy.clip(v + numpy.floor(numpy.random.normal(scale=2)), min_b, max_b))
    return v


def find_neighbours(solution):
    n = []
    for _ in range(len(solution) * int(1 / args.variable_change_probability) * 10):
        neighbour = [__single_value_gen(solution[i], args.min_bits_number, args.max_bits_number)
                     for i in range(len(solution))]
        n.append(neighbour)

    n.sort()
    return list(n for n, _ in itertools.groupby(n))


def infer_errors(bm: benchmarks.Benchmark, configs, data, mode: str or callable = 'nearest_n'):
    if type(mode) is str:
        mode = ei.infer_modes[mode]

    return mode(bm, configs, data)


def infer_examples_for_retraining(bm: benchmarks.Benchmark, session: training.TrainingSession, it):
    w = numpy.maximum(1e-6, numpy.abs(it.get_error_log() - numpy.log10(args.error)))

    neighbours = find_neighbours(it.config)
    neighbours_w = [w * (1 if bm.check_binary_relations_for(n) else .001) for n in neighbours]

    e, c = infer_errors(bm, neighbours, session.full_training_data)
    return ExamplesGenerator(it.config, neighbours, it.get_error_log(), e, it.get_error_class(), c, [w] + neighbours_w)


def ml_refinement(bm: benchmarks.Benchmark, regressor, classifier,
                  session: training.TrainingSession, examples: ExamplesGenerator):
    regr_target_label = 'reg'
    class_target_label = 'cls'

    df = examples.build_data_frame(regr_target_label, class_target_label)

    clfr_training = session.training_set
    clfr_training[regr_target_label] = session.regressor_target.values
    clfr_training[class_target_label] = session.classifier_target.values
    clfr_training = pandas.concat([clfr_training, df])

    clfr_training = clfr_training.drop_duplicates(subset=['var_{}'.format(i) for i in range(bm.vars_number)])

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

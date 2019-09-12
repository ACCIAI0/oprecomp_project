#!/usr/bin/env python
# -*- coding: utf-8 -*-

import warnings
warnings.filterwarnings('ignore')

import sys
import os
import datetime

from tensorflow.compat.v1 import logging

import utils
import argsmanaging
import benchmarks
import training
import optimization


def main(argv):
    # ArgumentsHolder containing all legal initialization params.
    args = argsmanaging.handle_args(argv)
    utils.print_n('\n[LOG] {}'.format(args))

    # Benchmarks information. Contains a relational graph among variables inside the benchmark program and the number
    # of them.
    utils.stop_w.start()
    bm = benchmarks.get_benchmark(args.benchmark)
    n = bm.vars_number
    _, t = utils.stop_w.stop()
    utils.print_n("[LOG] {} loaded in {:.3f}s ($green#{}$ variables)", bm.name, t, n)

    # Build training set and test set for a new training session
    utils.stop_w.start()
    session = training.create_training_session(bm, set_size=500)
    _, t = utils.stop_w.stop()
    utils.print_n("[LOG] Created first training session from dataset #{:d} in {:.3f}s ($green#{}$ entries for training,"
                  " $green#{}$ for test)", args.dataset_index, t, len(session.training_set),
                  len(session.test_set))

    # Train a regressor
    trainer = training.RegressorTrainer.create_for(args.regressor_type, session)
    utils.stop_w.start()
    regressor = trainer.create_regressor(bm)
    _, t = utils.stop_w.stop()
    print("[LOG] Regressor created in {:.3f}s".format(t))
    utils.stop_w.start()
    trainer.train_regressor(regressor, verbose=False)
    r_stats = trainer.test_regressor(bm, regressor)
    _, t = utils.stop_w.stop()
    utils.print_n("[LOG] First training of the regressor completed in {:.3f}s (MAE $green#{:.3f}$)", t, r_stats['MAE'])

    # Train a classifier
    utils.stop_w.start()
    trainer = training.ClassifierTrainer.create_for(args.classifier_type, session)
    classifier = trainer.create_classifier(bm)
    _, t = utils.stop_w.stop()
    print("[LOG] Classifier created in {:.3f}s".format(t))
    utils.stop_w.start()
    trainer.train_classifier(classifier)
    c_stats = trainer.test_classifier(bm, classifier)
    _, t = utils.stop_w.stop()
    utils.print_n("[LOG] First training of the classifier completed in {:.3f}s (accuracy $green#{:.3f}%$)", t,
                  c_stats['accuracy'] * 100)

    # Create a MP model
    utils.stop_w.start()
    optim_model = optimization.create_optimization_model(bm, regressor, classifier, limit_search_exp=6)
    _, t = utils.stop_w.stop()
    print("[LOG] Created an optimization model in {:.3f}s\n".format(t))

    # Solve optimization problem
    config, its = optimization.try_model(bm, optim_model, regressor, classifier, session)

    utils.print_n("[LOG] SOLUTION FOUND: $b#green#{}$", config)
    utils.print_n("[LOG] $b#cyan#Total execution time: {}s, search iterations: {:d}$\n",
                  datetime.timedelta(seconds=utils.stop_w.duration), its)

    if args.print_graph:
        bm.plot_var_graph()


'''
Entry point. Imports EML and calls to main function if this is main module.
'''
if __name__ == '__main__':
    # Remove annoying warning prints from output
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    logging.set_verbosity(logging.ERROR)

    # Main call
    main(sys.argv[1:])
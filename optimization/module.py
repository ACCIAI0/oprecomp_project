#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
import pandas

from optimization.iteration import Iteration
from optimization.model import refine_model, solve_model

from argsmanaging import args
import benchmarks
import training
import data_gen
import utils


def __log_iteration(it: Iteration, n, t):
    form = "$"
    source = "$b#FOUND$"
    if it.has_failed:
        form = "$yellow#"
        source = "$b#yellow#GENERATED$"

    utils.print_n("[OPT] Solution n. {:d} " + source + " in {:.3f}s:", n, t)

    target_label = "target error"
    error_label = "calculated error"
    predicted_label = "predicted error"
    log = "log({})"
    utils.print_n("[OPT] $green#{}  {}$  $blue#{}$  $green#{}  {}$", error_label, predicted_label,
                  log.format(target_label), log.format(error_label), log.format(predicted_label))

    pr = numpy.float_power(10, -it.get_predicted_error_log())

    formatted = "{:.3f}".format(-numpy.log10(args.error))
    l_target = (" " * (len(target_label) + 5 - len(formatted))) + formatted
    formatted = "{:.3e}".format(it.get_error())
    error = (" " * (len(error_label) - len(formatted))) + formatted
    formatted = "{:.3f}".format(it.get_error_log())
    l_error = (" " * (len(error_label) + 5 - len(formatted))) + formatted
    formatted = "{:.3e}".format(pr)
    predicted = (" " * (len(predicted_label) - len(formatted))) + formatted
    formatted = "{:.3f}".format(it.get_predicted_error_log())
    l_predicted = (" " * (len(predicted_label) + 5 - len(formatted))) + formatted
    utils.print_n("[OPT] " + form + "{}  {}  {}  {}  {}$".format(error, predicted, l_target, l_error, l_predicted))

    state = "$blue#FEASIBLE$" if it.is_feasible else "$red#NOT FEASIBLE$"
    utils.print_n("[OPT] Solution n. {:d} $b#cyan#{}$ is {}", n, it.config, state)
    print()


def __get_predictions(config, regr, classifier):
    conf_df = pandas.DataFrame.from_dict({'var_{}'.format(i): [config[i]] for i in range(len(config))})
    prediction_with_conf = regr.predict(conf_df)[0]
    class_pred_with_conf = classifier.predict(conf_df)[0]
    return prediction_with_conf[0], class_pred_with_conf


def __iterate(bm: benchmarks.Benchmark, mdl, regressor, classifier, previous_it: Iteration):
    opt_config = solve_model(mdl, bm)
    failed = False
    if opt_config is None:
        failed = True
        opt_config = numpy.random.randint(args.min_bits_number, args.max_bits_number, bm.vars_number)

    error = benchmarks.run_benchmark_with_config(bm, opt_config, args)
    predicted_error, predicted_class = __get_predictions(opt_config, regressor, classifier)
    return Iteration(opt_config, error, predicted_error, predicted_class, previous_it, failed)


def __execute_step(bm: benchmarks.Benchmark, mdl, regressor, classifier, previous: Iteration):
    utils.stop_w.start()
    it = __iterate(bm, mdl, regressor, classifier, previous)
    _, t = utils.stop_w.stop()
    __log_iteration(it, 0, t)
    return it


def try_model(bm: benchmarks.Benchmark, mdl, regressor, classifier, session: training.TrainingSession,
              max_iterations=100, refinement_steps=5):
    it = __execute_step(bm, mdl, regressor, classifier, None)

    current_refinement = 0
    while current_refinement < refinement_steps and it.iter_n <= max_iterations:
        best, _ = it.best_config_and_error
        if best is not None:
            current_refinement += 1
            utils.print_n("[OPT] $b#cyan#Refinement {}$", current_refinement)

        utils.stop_w.start()
        examples = data_gen.infer_examples(bm, session, it)
        _, t = utils.stop_w.stop()
        utils.print_n("[OPT] Inferred $green#{}$ more examples in {:.3f}s", len(examples), t)

        utils.stop_w.start()
        session, r_stats, c_stats = data_gen.ml_refinement(bm, regressor, classifier, session, examples)
        _, t = utils.stop_w.stop()
        utils.print_n("[OPT] Retrained regressor (MAE $green#{:.3f}$) and classifier "
                      "(accuracy $green#{:.3f}%$) in {:.3f}s", r_stats['MAE'], c_stats['accuracy'] * 100, t)

        utils.stop_w.start()
        refine_model(mdl, regressor, it, bm)
        _, t = utils.stop_w.stop()
        utils.print_n("[OPT] Refined model in {:.3f}s\n", t)

        if args.manual_toggled:
            input("\n[Press any button for next iteration]")

        it = __execute_step(bm, mdl, regressor, classifier, it)

    best, _ = it.best_config_and_error
    return best, it.iter_n - 1 - current_refinement

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import float_info

import pandas
import numpy

import data_gen
import benchmarks
from argsmanaging import args, Regressor, Classifier
import training
import utils

from docplex.mp import model
from eml.backend import cplex_backend
from eml.tree import embed as dt_embed
from eml.tree.reader import sklearn_reader
from eml.net import process, embed as nn_embed
from eml.net.reader import keras_reader

__max_target_error = numpy.ceil(-numpy.log10(1e-80))
__n_vars_bounds_tightening = 10
__bounds_opt_time_limit = 10
__classifier_threshold = .5


class Iteration:
    def __init__(self, config, error, predicted_error, predicted_class, previous_iteration, failed):
        self.__config = config
        self.__error = error
        self.__pError = predicted_error
        self.__pClass = predicted_class
        self.__previous = previous_iteration
        self.__p_best_cfg, self.__p_best_err = (None, 0) if self.__previous is None else self.__previous.get_best()
        self.__args = args
        self.__failed = failed

    def get_previous_iteration(self):
        return self.__previous

    def get_config(self):
        return self.__config

    def get_error(self):
        return self.__error

    def get_error_class(self):
        return int(self.__error >= self.__args.large_error_threshold)

    def get_error_log(self):
        return -numpy.log10(self.__error) if 0 != self.__error else float_info.min

    def get_predicted_error_log(self):
        return self.__pError

    def get_predicted_class(self):
        return self.__pClass

    def is_feasible(self):
        return self.get_error_log() >= -numpy.log10(self.__args.error)

    def get_delta_config(self):
        if self.__previous is None:
            return [0] * len(self.__config)
        return [i - j for i, j in zip(self.__previous.get_config(), self.__config)]

    def get_delta_error(self):
        if self.__previous is None:
            return 0
        return self.__previous.get_error() - self.__error

    def get_best(self):
        if self.__p_best_cfg is None:
            if self.is_feasible():
                return self.__config, self.__error
            else:
                return None, 0
        else:
            sum_c = sum(self.__config)
            sum_c_p = sum(self.__p_best_cfg)
            if self.is_feasible() and (sum_c < sum_c_p or (sum_c == sum_c_p and self.__error < self.__p_best_err)):
                return self.__config, self.__error
            else:
                return self.__p_best_cfg, self.__p_best_err

    def has_failed(self):
        return self.__failed


def __eml_regressor_nn(bm: benchmarks.Benchmark, regressor):
    regressor_em = keras_reader.read_keras_sequential(regressor)
    regressor_em.reset_bounds()
    for neuron in regressor_em.layer(0).neurons():
        neuron.update_lb(args.min_bits_number)
        neuron.update_ub(args.max_bits_number)

    process.ibr_bounds(regressor_em)

    if bm.vars_number > __n_vars_bounds_tightening:
        bounds_backend = cplex_backend.CplexBackend()
        process.fwd_bound_tighthening(bounds_backend, regressor_em, timelimit=__bounds_opt_time_limit)

    return regressor_em


__eml_regressors = {
    Regressor.NEURAL_NETWORK: __eml_regressor_nn
}


def __eml_classifier_dt(bm: benchmarks.Benchmark, classifier):
    classifier_em = sklearn_reader.read_sklearn_tree(classifier)
    for attr in classifier_em.attributes():
        classifier_em.update_lb(attr, args.min_bits_number)
        classifier_em.update_ub(attr, args.max_bits_number)

    return classifier_em


__eml_classifiers = {
    Classifier.DECISION_TREE: __eml_classifier_dt
}


def create_optimization_model(bm: benchmarks.Benchmark, regressor, classifier, robustness: int = 0, limit_search_exp=0):
    backend = cplex_backend.CplexBackend()
    mdl = model.Model()
    x_vars = [mdl.integer_var(lb=args.min_bits_number, ub=args.max_bits_number, name='x_{}'.format(i))
              for i in range(bm.vars_number)]

    # If it is a limited search in n orders of magnitudes, change the upper_bound to be -log(10e-(n + exp)) where exp is
    # the input parameter to calculate the error.
    upper_bound = __max_target_error
    if 0 != limit_search_exp:
        upper_bound = args.exponent + limit_search_exp

    # Moved this to be a lower bound instead of a constraint
    target_error_log = numpy.ceil(-numpy.log10(args.error))
    max_config = pandas.DataFrame.from_dict({'var_{}'.format(i): [args.max_bits_number]
                                             for i in range(bm.vars_number)})
    limit_predictable_error = regressor.predict(max_config)[0][0]
    if limit_predictable_error < target_error_log:
        robustness = -numpy.ceil(target_error_log - limit_predictable_error)

    y_var = mdl.continuous_var(lb=target_error_log + robustness, ub=upper_bound, name='y')

    bit_sum_var = mdl.integer_var(lb=args.min_bits_number * bm.vars_number,
                                  ub=args.max_bits_number * bm.vars_number, name='bit_sum')

    class_var = mdl.continuous_var(lb=0, ub=1, name='class')

    # Add relations from graph
    relations = bm.get_binary_relations()
    for vs, vg in relations['leq']:
        x_vs = mdl.get_var_by_name('x_{}'.format(vs.get_index()))
        x_vg = mdl.get_var_by_name('x_{}'.format(vg.get_index()))
        mdl.add_constraint(x_vs <= x_vg)
    for vt, vv in relations['cast']:
        x_vt = mdl.get_var_by_name('x_{}'.format(vt.get_index()))
        x_vv = [mdl.get_var_by_name('x_{}'.format(v.get_index())) for v in vv]
        mdl.add_constraint(mdl.min(x_vv) == x_vt)

    reg_em = __eml_regressors[args.regressor_type](bm, regressor)
    nn_embed.encode(backend, reg_em, mdl, x_vars, y_var, 'regressor')

    cls_em = __eml_classifiers[args.classifier_type](bm, classifier)
    dt_embed.encode_backward_implications(backend, cls_em, mdl, x_vars, class_var, 'classifier')
    mdl.add_constraint(class_var <= __classifier_threshold)
    mdl.add_constraint(bit_sum_var == sum(x_vars))

    mdl.minimize(mdl.sum(x_vars))

    mdl.set_time_limit(30)
    return mdl


def __refine_and_solve_mp(bm: benchmarks.Benchmark, mdl, n_iter, it: Iteration):
    # Remove an infeasible solution from the solutions pool
    if it is not None and not it.has_failed() and not it.is_feasible():
        bin_vars_cut_vals = []
        for i in range(len(it.get_config())):
            x_var = mdl.get_var_by_name('x_{}'.format(i))
            bin_vars_cut_vals.append(mdl.binary_var(name='bvcv_{}_{}'.format(n_iter, i)))
            mdl.add(mdl.if_then(x_var == it.get_config()[i], bin_vars_cut_vals[i] == 1))
        mdl.add_constraint(sum(bin_vars_cut_vals) <= 1)

    # Add a constraint to force the model to find better solutions than the one currently given as the best one
    if it is not None:
        best, _ = it.get_best()
        if best is not None:
            mdl.add_constraint(mdl.get_var_by_name('bit_sum') <= sum(best) - 1)

    solution = mdl.solve()
    opt_config = None
    if solution is not None:
        opt_config = [int(solution['x_{}'.format(i)]) for i in range(bm.vars_number)]
    return opt_config, mdl


def __get_predictions(config, regr, classifier):
    conf_df = pandas.DataFrame.from_dict({'var_{}'.format(i): [config[i]] for i in range(len(config))})
    prediction_with_conf = regr.predict(conf_df)[0]
    class_pred_with_conf = classifier.predict(conf_df)[0]
    return prediction_with_conf[0], class_pred_with_conf


def __iterate(bm: benchmarks.Benchmark, mdl, regressor, classifier, previous_it: Iteration = None, n_iter=0):
    opt_config, mdl = __refine_and_solve_mp(bm, mdl, n_iter, previous_it)
    failed = False
    if opt_config is None:
        failed = True
        opt_config = numpy.random.randint(args.min_bits_number, args.max_bits_number, bm.vars_number)

    error = benchmarks.run_benchmark_with_config(bm, opt_config, args)
    predicted_error, predicted_class = __get_predictions(opt_config, regressor, classifier)
    return mdl, Iteration(opt_config, error, predicted_error, predicted_class, previous_it, failed)


def __log_iteration(it: Iteration, n, t):
    if it.has_failed():
        utils.print_n("[OPT] $yellow#{}$", "Generated solution n. " + str(n))
    else:
        print("[OPT] Solution n. {:d} found in {:.3f}s:".format(n, t))
    target_label = "target error"
    error_label = "calculated error"
    predicted_label = "predicted error"
    log = "log({})"

    utils.print_n("[OPT] $green#{}  {}$  |  $blue#{}$  $green#{}  {}$", error_label, predicted_label,
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
    utils.print_n("[OPT] {}  {}  |  {}  {}  {}".format(error, predicted, l_target, l_error, l_predicted))

    state = "$blue#FEASIBLE$" if it.is_feasible() else "$red#NOT FEASIBLE$"
    utils.print_n("[OPT] Solution n. {:d} $b#cyan#{}$ is {}", n, it.get_config(), state)
    print()


def try_model(bm: benchmarks.Benchmark, mdl, regressor, classifier, session: training.TrainingSession,
              max_iterations=100, refinement_steps=5):
    utils.stop_w.start()
    mdl, it = __iterate(bm, mdl, regressor, classifier)
    _, t = utils.stop_w.stop()
    __log_iteration(it, 0, t)
    iterations = 1
    current_refinement = 0
    while current_refinement < refinement_steps and iterations <= max_iterations:
        best, _ = it.get_best()
        if best is not None:
            current_refinement += 1
            utils.print_n("[OPT] $b#cyan#Refinment {}$", current_refinement)

        utils.stop_w.start()
        examples = data_gen.infer_examples(bm, it)
        _, t = utils.stop_w.stop()
        utils.print_n("[OPT] Inferred $green#{}$ more examples in {:.3f}s", len(examples), t)

        utils.stop_w.start()
        session, r_stats, c_stats = data_gen.ml_refinement(bm, regressor, classifier, session, examples)
        _, t = utils.stop_w.stop()
        utils.print_n("[OPT] Retrained regressor (MAE $green#{:.3f}$) and classifier "
                      "(accuracy $green#{:.3f}%$) in {:.3f}s", r_stats['MAE'], c_stats['accuracy'] * 100, t)

        utils.stop_w.start()
        mdl, it = __iterate(bm, mdl, regressor, classifier, it, iterations)
        _, t = utils.stop_w.stop()
        __log_iteration(it, iterations, t)
        iterations += 1

    best, _ = it.get_best()
    return best, iterations - 1 - current_refinement

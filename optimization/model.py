#!/usr/bin/env python
# -*- coding: utf-8 -*-

from optimization.iteration import Iteration

import benchmarks
from argsmanaging import args, Classifier, Regressor

import numpy
import pandas

from docplex.mp import model
from eml.backend import cplex_backend
from eml.tree import embed as dt_embed
from eml.tree.reader import sklearn_reader
from eml.net import process, embed as nn_embed
from eml.net.reader import keras_reader


__n_vars_bounds_tightening = 10
__bounds_opt_time_limit = 10


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


def __embed_ml_models(bm: benchmarks.Benchmark, mdl: model.Model, regressor, classifier):
    backend = cplex_backend.CplexBackend()
    x_vars = [mdl.get_var_by_name('x_{}'.format(i)) for i in range(bm.vars_number)]
    y_var = mdl.get_var_by_name('y')
    class_var = mdl.get_var_by_name('class')
    reg_em = __eml_regressors[args.regressor_type](bm, regressor)
    nn_embed.encode(backend, reg_em, mdl, x_vars, y_var, 'regressor')

    cls_em = __eml_classifiers[args.classifier_type](bm, classifier)
    dt_embed.encode_backward_implications(backend, cls_em, mdl, x_vars, class_var, 'classifier')


def create_optimization_model(bm: benchmarks.Benchmark, regressor, classifier, iteration: Iteration = None):
    mdl = model.Model()
    x_vars = [mdl.integer_var(lb=args.min_bits_number, ub=args.max_bits_number, name='x_{}'.format(i))
              for i in range(bm.vars_number)]

    max_config = pandas.DataFrame.from_dict({'var_{}'.format(i): [args.max_bits_number] for i in range(bm.vars_number)})
    upper_bound = regressor.predict(max_config)[0][0]

    # If it is a limited search in n orders of magnitudes, change the upper_bound to be -log(10e-(n + exp)) where exp is
    # the input parameter to calculate the error.
    if 0 != args.search_limit:  # and upper_bound > args.exponent + args.search_limit:
        upper_bound = args.exponent + args.search_limit

    if upper_bound < args.error_log:
        raise ValueError("Calculated upper bound {:.3f} is higher than the target".format(upper_bound))

    y_var = mdl.continuous_var(lb=numpy.ceil(args.error_log), ub=numpy.ceil(upper_bound), name='y')

    bit_sum_var = mdl.integer_var(lb=args.min_bits_number * bm.vars_number,
                                  ub=args.max_bits_number * bm.vars_number, name='bit_sum')

    class_var = mdl.continuous_var(lb=0, ub=1, name='class')

    # Adding relations from graph
    relations = bm.get_binary_relations()
    for vs, vg in relations['leq']:
        x_vs = mdl.get_var_by_name('x_{}'.format(vs.index))
        x_vg = mdl.get_var_by_name('x_{}'.format(vg.index))
        mdl.add_constraint(x_vs <= x_vg)
    for vt, vv in relations['cast']:
        x_vt = mdl.get_var_by_name('x_{}'.format(vt.index))
        x_vv = [mdl.get_var_by_name('x_{}'.format(v.index)) for v in vv]
        mdl.add_constraint(mdl.min(x_vv) == x_vt)

    # Add a constraint to force the model to find better solutions than the one currently given as the best one
    if iteration is not None:
        best, _ = iteration.best_config_and_error
        if best is not None:
            mdl.add_constraint(mdl.get_var_by_name('bit_sum') <= mdl.sum(best) - 1)

    # Remove any infeasible solution from the solutions pool
    if iteration is not None:
        for it in iteration:
            if it is not None and not it.is_feasible:
                bin_vars_cut_vals = []
                for i in range(len(it.config)):
                    x_var = mdl.get_var_by_name('x_{}'.format(i))
                    bin_vars_cut_vals.append(mdl.binary_var(name='bvcv_{}_{}'.format(it.iter_n, i)))
                    mdl.add(mdl.if_then(x_var == it.config[i], bin_vars_cut_vals[i] == 1))
                mdl.add_constraint(mdl.sum(bin_vars_cut_vals) <= 1)

    # Embed the ML models in the MP
    __embed_ml_models(bm, mdl, regressor, classifier)

    mdl.add_constraint(class_var <= .5)
    mdl.add_constraint(bit_sum_var == mdl.sum(x_vars))

    mdl.minimize(mdl.sum(x_vars))

    mdl.set_time_limit(30)

    return mdl


def solve_model(mdl: model.Model, bm: benchmarks.Benchmark):
    solution = mdl.solve()
    opt_config = None
    prediction = None
    class_prediction = None
    if solution is not None:
        opt_config = [int(solution['x_{}'.format(i)]) for i in range(bm.vars_number)]
        prediction = solution['y']
        class_prediction = solution['class']
    return opt_config, prediction, None if class_prediction is None else int(round(class_prediction, 0))

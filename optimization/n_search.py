#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy

import benchmarks
import training
import data_gen
from argsmanaging import args
import utils


def __v1(bm: benchmarks.Benchmark, session: training.TrainingSession, best, log):
    for iteration in range(args.steps):
        utils.stop_w.start()
        s_b = sum(best)
        nbrs = list(filter(lambda c: bm.check_binary_relations_for(c) and sum(c) < s_b, data_gen.find_neighbours(best)))
        if 0 == len(nbrs):
            utils.print_n("[OPT] $b#yellow#No lower-sum neighbours found$")
            _, t = utils.stop_w.stop()
            break

        utils.print_n("[OPT] $b#cyan#Neighbourhood refinement {}$", iteration + 1)

        errs, _ = data_gen.infer_errors(bm, nbrs, session.full_training_data, 'rbf')
        filtered = []
        for i in range(len(nbrs)):
            if args.error_log <= errs[i]:
                filtered.append(nbrs[i])
        nbrs = sorted(filtered, key=sum)
        _, t = utils.stop_w.stop()
        if 0 == len(nbrs):
            utils.print_n("[OPT] No better neighbours found\n")
            break

        best = nbrs[0]
        if log is not None:
            log.insert_neighbour_search(len(nbrs), best)
        utils.print_n("[OPT] found better neighbour $b#cyan#{}$ after {:.3f}s\n", best, t)
    return best


def __v2(bm: benchmarks.Benchmark, session: training.TrainingSession, best, log):
    refs = [best]
    for iteration in range(args.steps):
        utils.stop_w.start()
        best = refs[len(refs) - 1]
        s_b = sum(best)
        nbrs = list(filter(lambda c: sum(c) < s_b, data_gen.find_neighbours(best)))
        if 0 == len(nbrs):
            utils.print_n("[OPT] $b#yellow#No lower-sum neighbours found$")
            _, t = utils.stop_w.stop()
            break

        utils.print_n("[OPT] $b#cyan#Neighbourhood refinement {}$", iteration + 1)

        errs, _ = data_gen.infer_errors(bm, nbrs, session.full_training_data, 'rbf')
        filtered = []
        for i in range(len(nbrs)):
            if args.error_log <= errs[i]:
                filtered.append(nbrs[i])
        nbrs = sorted(filtered, key=sum)
        _, t = utils.stop_w.stop()
        if 0 == len(nbrs):
            utils.print_n("[OPT] No better neighbours found\n")
            break

        best = nbrs[0]
        if log is not None:
            log.insert_neighbour_search(len(nbrs), best)
        utils.print_n("[OPT] found better neighbour $b#cyan#{}$ after {:.3f}s\n", best, t)
        refs.append(best)

    # Check the result. If none is actually better it settles for the initial best
    utils.print_n("[LOG] Checking results...")

    i = len(refs) - 1
    while -numpy.log10(benchmarks.run_benchmark_with_config(bm, refs[i], args)) < args.error_log and 0 != i:
        i -= 1
    return refs[i]


vs = {
    0: lambda bm, s, b, l: b,
    1: __v1,
    2: __v2
}


def search(bm: benchmarks.Benchmark, session: training.TrainingSession, best, log, version):
    print(version)
    return vs[version](bm, session, best, log)

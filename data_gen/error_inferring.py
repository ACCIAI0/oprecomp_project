#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum

import pandas
import numpy
from sklearn import neighbors as nbrs
from scipy import interpolate

import benchmarks
from argsmanaging import args


def __to_tuple(l):
    e = []
    c = []
    for p in l:
        e.append(p[0])
        c.append(int(round(p[1])))
    return e, c


def nearest_neighbours(bm: benchmarks.Benchmark, configs, data: pandas.DataFrame):
    knn = nbrs.KNeighborsRegressor(n_neighbors=5, weights='distance')
    knn.fit(data[['var_{}'.format(i) for i in range(bm.vars_number)]], data[['err_log', 'class']])
    return __to_tuple(knn.predict(numpy.array(configs)))


def linear_interpolation(bm: benchmarks.Benchmark, configs, data: pandas.DataFrame):
    i = interpolate.LinearNDInterpolator(data[['var_{}'.format(i) for i in range(bm.vars_number)]].to_numpy().tolist(),
                                         data[['err_log', 'class']].to_numpy().tolist())
    return __to_tuple(i(configs))


def rbf(bm: benchmarks.Benchmark, configs, data: pandas.DataFrame):
    data.drop_duplicates()
    array = [data['var_{}'.format(i)].tolist() for i in range(bm.vars_number)]
    array.append(data['err_log'].tolist())
    rbfi = interpolate.Rbf(*array)
    array = [[c[i] for c in configs] for i in range(bm.vars_number)]
    result = list(rbfi(*array))
    return result, [(1 if args.large_error_threshold <= r else 0) for r in result]


infer_modes = {
    'nearest_n': nearest_neighbours,
    'linear': linear_interpolation,
    'rbf': rbf
}

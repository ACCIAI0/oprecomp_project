#!/usr/bin/env python
# -*- coding: utf-8 -*-

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


def __nearest_neighbours(bm: benchmarks.Benchmark, configs, data: pandas.DataFrame):
    knn = nbrs.KNeighborsRegressor(n_neighbors=5, weights='distance')
    knn.fit(data[['var_{}'.format(i) for i in range(bm.vars_number)]], data[['err_log', 'class']])
    return __to_tuple(knn.predict(numpy.array(configs)))


# Don't use, too slow
def __linear_interpolation(bm: benchmarks.Benchmark, configs, data: pandas.DataFrame):
    i = interpolate.LinearNDInterpolator(data[['var_{}'.format(i) for i in range(bm.vars_number)]].to_numpy().tolist(),
                                         data[['err_log', 'class']].to_numpy().tolist())
    return __to_tuple(i(configs))


def __rbf(bm: benchmarks.Benchmark, configs, data: pandas.DataFrame):
    data.drop_duplicates()
    array = [data['var_{}'.format(i)].tolist() for i in range(bm.vars_number)]
    array.append(data['err_log'].tolist())
    rbfi = interpolate.Rbf(*array)
    array = [[c[i] for c in configs] for i in range(bm.vars_number)]
    result = list(rbfi(*array))
    return result, [(1 if args.large_error_threshold <= r else 0) for r in result]


infer_modes = {
    'nearest_n': __nearest_neighbours,
    'linear': __linear_interpolation,
    'rbf': __rbf
}

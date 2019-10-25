#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import float_info

import numpy
import pandas
from sklearn import model_selection

import benchmarks
from training.session import TrainingSession
from argsmanaging import args


__dataset_home = "datasets/"


def __initialize_mean_std(bm: benchmarks.Benchmark, label: str, log_label: str, clamp: bool = True):
    data_file = 'exp_results_{}.csv'.format(bm.name)

    df = pandas.read_csv(__dataset_home + data_file, sep=';')
    columns = [x for x in filter(lambda l: 'var_' in l or label == l, df.columns)]
    df = df[columns]

    if clamp:
        df.loc[df[label] > args.large_error_threshold, label] = args.large_error_threshold
    df[log_label] = [float_info.min if 0 == x else -numpy.log10(x) for x in df[label]]

    return df


def __select_subset(df: pandas.DataFrame, error_label: str, size: int):
    n_large_errors = len(df[df[error_label] >= args.large_error_threshold])
    ratio = n_large_errors / len(df)

    if 0 == ratio:
        return df.sample(size)
    acc = 0
    df_t = pandas.DataFrame()
    while acc < ratio:
        if size > len(df):
            size = len(df) - 1
        df_t = df.sample(size)
        acc = len(df_t[df_t[error_label] >= args.large_error_threshold]) / len(df_t)
    return df_t


def __select_in(df: pandas.DataFrame, min_sum: int, max_sum: int, size: int):
    df_f = df[(df.sum(axis=1) >= min_sum) & (df.sum(axis=1) <= max_sum)]
    return df_f.sample(size) if size < len(df_f) else df_f


def __select_categorized_subset(bm: benchmarks.Benchmark, df: pandas.DataFrame, size: int):
    n_groups = 4
    min_sum = args.min_bits_number * bm.vars_number
    max_sum = args.max_bits_number * bm.vars_number
    delta = int((max_sum - min_sum) / n_groups)

    df_r = pandas.DataFrame()
    for i in range(n_groups):
        lb = min_sum + delta * i
        ub = lb + delta - 1
        df_r = pandas.concat([df_r, __select_in(df, lb, ub, int(size * (4 - i) / 10.0))])
    return df_r


def create_training_session(bm: benchmarks.Benchmark, set_size: int = 500) -> TrainingSession:
    label = 'err_ds_{}'.format(args.dataset_index)
    log_label = 'err_log_ds_{}'.format(args.dataset_index)
    class_label = 'class_ds_{}'.format(args.dataset_index)

    # Initialize a pandas DataFrame from file, clamping error values and calculating log errors
    df = __initialize_mean_std(bm, label, log_label)
    # Keep entries with all non-zero values
    df = df[(df != 0).all(1)]
    # Selects a subset with a balanced ratio between high and low error values
    df_r = __select_subset(df, label, int(set_size / 2))
    df_f = __select_categorized_subset(bm, df, int(set_size / 2))
    df = pandas.concat([df_r, df_f], ignore_index=True)
    # Calculates the classifier class column
    df[class_label] = df.apply(lambda e: int(e[label] >= args.large_error_threshold), axis=1)
    # Delete err_ds_<index> column as it is useless from here on
    del df[label]
    # Drop all duplicates if any
    df = df.drop_duplicates(subset=['var_{}'.format(i) for i in range(bm.vars_number)])
    # Split in train set and test set
    train, test = model_selection.train_test_split(df, test_size=.1)

    return TrainingSession(train, test, log_label, class_label)

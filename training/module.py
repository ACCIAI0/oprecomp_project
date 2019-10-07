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


def __select_subset(df: pandas.DataFrame, threshold: float, error_label: str, size: int):
    n_large_errors = len(df[df[error_label] >= threshold])
    ratio = n_large_errors / len(df)

    if 0 == ratio:
        return df.sample(size)
    acc = 0
    df_t = pandas.DataFrame()
    while acc < ratio:
        if size > len(df):
            size = len(df) - 1
        df_t = df.sample(size)
        acc = len(df_t[error_label] >= threshold) / len(df_t)
    return df_t


def create_training_session(benchmark: benchmarks.Benchmark,
                            initial_sampling_size: int = 3000, set_size: int = 500) -> TrainingSession:
    label = 'err_ds_{}'.format(args.dataset_index)
    log_label = 'err_log_ds_{}'.format(args.dataset_index)
    class_label = 'class_ds_{}'.format(args.dataset_index)

    # Initialize a pandas DataFrame from file, clamping error values and calculating log errors
    df = __initialize_mean_std(benchmark, label, log_label)
    # Keep entries with all non-zero values
    df = df[(df != 0).all(1)]
    # Selects a subset with a balanced ratio between high and low error values
    df = __select_subset(df, args.large_error_threshold, label, initial_sampling_size)
    # Reset indexes to start from 0
    df = df.reset_index(drop=True)
    # Calculates the classifier class column
    df[class_label] = df.apply(lambda e: int(e[label] >= args.large_error_threshold), axis=1)
    # Delete err_ds_<index> column as it is useless from here on
    del df[label]
    # Split in train set and test set
    train, test = model_selection.train_test_split(df, test_size=(len(df) - set_size) / len(df))

    return TrainingSession(train, test, log_label, class_label)

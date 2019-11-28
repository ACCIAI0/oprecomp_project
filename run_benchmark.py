#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import benchmarks
import argsmanaging


def main(argv):
    args = argsmanaging.handle_args(['-bm', argv[0], '-exp', argv[1]])
    bm = benchmarks.get_benchmark(argv[0])
    configs = [[i] * bm.vars_number for i in [4, 9, 20, 38, 53]]
    errs = {}
    for config in configs:
        errs[config[0]] = benchmarks.run_benchmark_with_config(bm, config, args)
    print(errs)


if __name__ == '__main__':
    main(sys.argv[1:])

#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Relater:
    def __init__(self, name: str, var_relations: list, check):
        self.__name = name
        self.__varRels = var_relations
        self.__check = check

    def __len__(self):
        return len(self.__varRels)

    def __getitem__(self, i):
        return self.__varRels[i]

    def __str__(self):
        return self.__name + ": " + str(self.__varRels)

    def __repr__(self):
        return self.__str__()

    @property
    def name(self):
        return self.__name

    def check_config(self, config: list):
        result = True
        for t in self.__varRels:
            second = t[1]
            if type(second) is not list:
                second = [second]
            result = result and self.__check(config[t[0].index], [config[i.index] for i in second])
            if not result:
                break
        return result

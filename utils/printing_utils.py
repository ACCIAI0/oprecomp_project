#!/usr/bin/env python
# -*- coding: utf-8 -*-

import colorama
import re


class FormatError(RuntimeError):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


formats = {
    'b': str(colorama.Style.BRIGHT),
    'd': str(colorama.Style.DIM),
    'green': str(colorama.Fore.GREEN),
    'cyan': str(colorama.Fore.CYAN),
    'blue': str(colorama.Fore.BLUE),
    'red': str(colorama.Fore.RED),
    'yellow': str(colorama.Fore.YELLOW),
    'black': str(colorama.Fore.BLACK),
    'white': str(colorama.Fore.WHITE),
    'magenta': str(colorama.Fore.MAGENTA),
    '_green': str(colorama.Back.GREEN),
    '_cyan': str(colorama.Back.CYAN),
    '_blue': str(colorama.Back.BLUE),
    '_red': str(colorama.Back.RED),
    '_yellow': str(colorama.Back.YELLOW),
    '_black': str(colorama.Back.BLACK),
    '_white': str(colorama.Back.WHITE),
    '_magenta': str(colorama.Back.MAGENTA)
}


def __generate_format(token):
    string = token.replace('$', '')
    tkns = re.split('#', string)
    result = ""
    for i in range(len(tkns)):
        if i == len(tkns) - 1:
            result += tkns[i]
        else:
            result += formats[tkns[i]]
    return result + str(colorama.Style.RESET_ALL)


def str_len(v, format):
    return len(format.format(v))


def print_n(string, *args):
    tkns = re.split("(\$[^\$]*\$)", string.format(*args))
    result = ""
    for t in tkns:
        result += t if not t.startswith('$') else __generate_format(t)
    print(result)


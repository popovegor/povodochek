#!/usr/bin/python
# -*- coding: utf-8 -*-


def num(value, default = None):
    # print(type(value))
    if (isinstance(value, str) or  isinstance(value, unicode)) and value.isdigit():
        return int(value)
    elif isinstance(value, int):
        return value
    return default
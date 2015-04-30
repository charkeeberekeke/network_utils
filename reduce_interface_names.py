#!/usr/bin/python

import os
import re
from string import maketrans, translate

IFACE_CHARS = r'^([a-zA-Z-]*)'
IFACE_DELIMS = '/:'

def breakdown(iface):
    _iface = re.sub(IFACE_CHARS, r'\1 ', iface)
    _iface = translate(_iface, maketrans(IFACE_DELIMS, " "*len(IFACE_DELIMS)))
    return _iface.split()

def insert_in_range(base, new):
    _new = int(new)
    if "-" in base:
        a, z = map(int, base.split("-"))
        if _new > z:
            if _new - z > 1:
                ret = base + "," + new
            else:
                ret = str(a) + "-" + new
        elif _new < a:
            if a - _new > 1:
                ret = new + "," + base
            else:
                ret = new + "-" + str(z)
        else:
            return base
    else:
        _base = int(base)
        if _new > _base:
            z, a = _new, _base
        else:
            z, a = _base, _new
        if z - a > 1:
            ret = str(a) + "," + str(z)
        else:
            ret = str(a) + "-" + str(z)
    return ret

def reduce(base, new):
    _new = breakdown(new)
    _base = base.split(",")
    #insert = True
    for i in range(len(_base)):
        _b = breakdown(_base[i])
        if len(_b) != len(_new):
            continue
        if any([l[0] != l[1] for l in zip(_b, _new)[:-1]]):
            continue
        else:
            _b[-1] = insert_in_range(_b[-1], _new[-1])
            _base[i] = "".join(_b) # need to insert original delimiters
            return ",".join(_base)
    _base.append(new)
    return ",".join(_base)


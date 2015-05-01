#!/usr/bin/python

import os
import re
from string import maketrans, translate
from operator import itemgetter
from itertools import groupby

IFACE_DELIMS = '(^[a-zA-Z-]+|/|:)'

def breakdown(iface):
    _iface = re.sub(IFACE_DELIMS, r' \1 ', iface).strip()
    return _iface.split()

def to_range(s):
    if "-" in s:
        x, y = map(int, s.split("-"))
        return range(x, y+1)
    else:
        return [int(s)]

def from_range(li):
    s = []
    for l in li:
        if len(l) == 1:
            s.append(str(l[0]))
        else:
            s.append("%s-%s" % (str(l[0]), str(l[-1])))
    return ",".join(s)

def insert_in_range(base, new):
    tmp = []
    ranges = []
    for i in base.split(","):
        tmp.extend(to_range(i))
    tmp.append(int(new))
    tmp.sort()
    tmp = list(set(tmp)) # remove duplicates
    ranges = []
    for k, g in groupby(enumerate(tmp), lambda (i, x): i-x):
        ranges.append(map(itemgetter(1), g))
    return from_range(ranges)

def reduce_iface(base, new):
    _new = breakdown(new)
    _base = (base != "") and base.split(";") or []
    for i in range(len(_base)):
        _b = breakdown(_base[i])
        if len(_b) != len(_new):
            continue
        if any([l[0] != l[1] for l in zip(_b, _new)[:-1]]):
            continue
        else:
            _b[-1] = insert_in_range(_b[-1], _new[-1])
            _base[i] = "".join(_b)
            return ";".join(_base)
    _base.append(new)
    return ";".join(_base)


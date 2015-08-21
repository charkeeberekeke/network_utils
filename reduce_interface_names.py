#!/usr/bin/python

import os
import re
from string import maketrans, translate
from operator import itemgetter
from itertools import groupby

IFACE_DELIMS = '(^[a-zA-Z-]+|/|:)'
# '-' character is used in reduced interface mode to denote range, eg. Fa0/1-4
# '-' is currently not used as an iface delimiter because of this, may cause problems
# for interface names that use - as delimiter, eg. Junos
# other possible iface delimiters, .

REDUCED_IFACES_DELIM = ';'
IFACE_RANGE = '-'
IFACE_RANGE_DELIM = ','

def breakdown(iface):
    """
    Splits interface name into logical parts, including delimiter
    eg. 
    Vlan1 = ["Vlan", "1"]
    Fastethernet0/24 = ['Fastethernet', '0', '/', '24']
    """
    _iface = re.sub(IFACE_DELIMS, r' \1 ', iface).strip()
    return _iface.split()

def to_range(s):
    """
    Convert x-y or x in string format to corresponding range
    eg.
    1-3 = [1,2,3]
    1 = [1]
    """
    if IFACE_RANGE in s:
        x, y = map(int, s.split(IFACE_RANGE))
        return range(x, y+1)
    else:
        return [int(s)]

def from_range(li):
    """
    Accepts list of ranges, returns ranges in string x-y format delimited by comma
    eg. 
    [[1,2,3],[5]] = '1-3,5'
    """
    s = []
    for l in li:
        if len(l) == 1:
            s.append(str(l[0]))
        else:
            s.append("%s-%s" % (str(l[0]), str(l[-1])))
    return IFACE_RANGE_DELIM.join(s)

def insert_in_range(base, new):
    """
    Inserts a new integer (new:int) within a list of integers (base:string)
    formatted as eg. [1,2,4,5,6,8,9,10] => 1-2,4,5-6,8,9-10
    and generates a new list with the same format as base
    eg. base = "5-9,12-15,17,19-21", new = 10, out = "5-10,12-15,17,19-21"
    """
    tmp = []
    ranges = []
    for i in base.split(IFACE_RANGE_DELIM):
        tmp.extend(to_range(i))
    tmp.append(int(new))
    tmp.sort()
    tmp = list(set(tmp)) # remove duplicates
    ranges = []
    # breaks list of integers into groups of consecutive integers
    for k, g in groupby(enumerate(tmp), lambda (i, x): i-x):
        #k is key value from groupby key fxn which is difference
        #b/w list index & value
        #extract value from (k,v) tuple in g using itemgetter
        ranges.append(map(itemgetter(1), g))
    #convert list of integers into condensed string format
    return from_range(ranges)

def reduce_iface(base, new):
    """
    Add new iface (new:string) to an iface (base:string) in a reduced format
    eg.
    base = "Fastethernet0/5-12,16-19;Vlan100,120,700;Loopback0"
    new = "Fastethernet0/14"
    reduce_iface(base, new) = "Fastethernet0/5-12,14,16-19;Vlan100,120,700;Loopback0"
    """
    _new = breakdown(new)
    _base = (base != "") and base.split(REDUCED_IFACES_DELIM) or []
    for i in range(len(_base)): #iterate over all ifaces in base
        _b = breakdown(_base[i])
        # exit if length of broken-down base iface is not equal to new iface
        if len(_b) != len(_new):
            continue
        # exit if any of the logical parts of the base and new iface, except for the last part,
        # are not equal
        if any([l[0] != l[1] for l in zip(_b, _new)[:-1]]):
            continue
        # insert new iface into base iface then return new reduced interfaces
        else:
            _b[-1] = insert_in_range(_b[-1], _new[-1])
            _base[i] = "".join(_b)
            return REDUCED_IFACES_DELIM.join(_base)
     # if new doesn't match any of the base ifaces, append into base
    _base.append(new)
    return REDUCED_IFACES_DELIM.join(_base)

def reduce_iface_2(ifaces):
    """
    Wrapper for reduce_iface, takes a single list of interface names
    and outputs a reduced interface list
    """
    tmp = ""
    ifaces.sort()
    for iface in ifaces:
       tmp = reduce_iface(tmp, iface)
    return tmp

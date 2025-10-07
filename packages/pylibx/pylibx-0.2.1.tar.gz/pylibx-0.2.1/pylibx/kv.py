# -*- coding: utf-8 -*-

import os

def kv_read(filename):
    ret = {}
    if not os.path.exists(filename):
        return ret
    with open(filename, 'r') as f:
        lines = f.readlines()
        for s in lines:
            s = s.strip()
            if not s:
                continue
            p = s.find('=')
            if p <= 0:
                continue
            k = s[0:p].strip()
            v = s[p + 1:].strip()
            if not k or not v:
                continue
            ret[k] = v
    return ret


def kv_write(filename, arr):
    with open(filename, 'w') as f:
        for k, v in arr.items():
            f.write("{0} = {1}\n".format(k, v))


def kv_get(filename, key):
    arr = kv_read(filename)
    return arr.get(key)


def kv_set(filename, key, val):
    arr = kv_read(filename)
    arr[key] = val
    kv_write(filename, arr)
# -*- coding: utf-8 -*-


import os
import sys
import zlib

def crc32(filename):
    block_size = 1024 * 1024
    crc = 0

    if not os.path.exists(filename):
        return crc
    with open(filename, 'rb') as f:
        while True:
            buffer = f.read(block_size)
            if len(buffer) == 0:  # EOF or file empty. return hashes
                if sys.version_info[0] < 3 and crc < 0:
                    crc += 2 ** 32
                return crc
            crc = zlib.crc32(buffer, crc)
    return crc


def cksum_read(sum_file):
    cksum = {}
    if not os.path.exists(sum_file):
        return cksum

    cols = []
    with open(sum_file, 'r') as f:
        lines = f.readlines()
        for s in lines:
            s = s.strip()
            if not s:
                continue
            arr = s.split(',')
            if not cols:
                for x in arr:
                    cols.append(x)
                continue

            if len(arr) != len(cols):
                continue

            fn = ''
            val = {}
            i = 0
            for x in arr:
                if not fn:
                    fn = x
                else:
                    val[cols[i]] = x
                i += 1
            cksum[fn] = val
    return cksum


def cksum_write(sum_file, cksum):
    if not cksum:
        if os.path.exists(sum_file):
            os.unlink(sum_file)
        return

    with open(sum_file, 'w') as f:
        f.write("filename,mtime,size,crc32\n")
        si = sorted(cksum.items(), key=lambda item: item[0])
        for sv in si:
            k = sv[0]
            v = sv[1]
            f.write("{0},{1},{2},{3}\n".format(k, v['mtime'], v['size'], v['crc32']))


def cksum_stat(file_path):
    fs = os.stat(file_path)
    val = dict()
    val['mtime'] = str(int(fs.st_mtime))
    val['size'] = str(int(fs.st_size))
    val['crc32'] = hex(crc32(file_path))[2:].zfill(8)
    return val


def cksum_clr(sum_file, filename):
    cksum = cksum_read(sum_file)
    del cksum[filename]
    cksum_write(sum_file, cksum)


def cksum_set(sum_file, filename):
    val = cksum_stat(os.path.join(os.path.dirname(sum_file), filename))
    cksum = cksum_read(sum_file)
    cksum[filename] = val
    cksum_write(sum_file, cksum)


def cksum_get(sum_file, filename):
    cksum = cksum_read(sum_file)
    return cksum.get(filename)
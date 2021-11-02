#!/usr/bin/env python

from __future__ import print_function
from pathlib import Path

import argparse
import fileinput
import json
import logging

class Flattener:
    def __init__(self, delimiter="_"):
        self.delimiter = delimiter

    def flatten(self, data, out=None, prefix=None):
        out = {} if out is None else out
        prefix = [] if prefix is None else prefix

        if isinstance(data, dict):
            for k,value in data.items():
                self.flatten(value, out, prefix + [k])
        elif isinstance(data, list):
            for counter, value in enumerate(data):
                self.flatten(value, out, prefix + [counter])
        else:
            key = self.delimiter.join([str(s) for s in prefix])
            logging.debug(f"writing {data} to {key}")
            out[key] = data
        return out

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('-f', '--file-prefix', action='store_true',
            help='use the filename as a prefix')
    p.add_argument('-p', '--path-prefix', action='store_true',
            help='use the path as a prefix')
    p.add_argument('input', nargs='*', help='input files, or stdin')
    return p.parse_args()

def run():
    opts = parse_args()
    flattener = Flattener()
    for line in fileinput.input(opts.input):
        data = json.loads(line.strip())
        prefix=None
        if opts.file_prefix:
            prefix = Path(fileinput.filename()).stem()
        elif opts.path_prefix:
            p = Path(fileinput.filename())
            prefix = p.parent / p.stem
        flattened = flattener.flatten(data, prefix=[str(prefix)])
        print(json.dumps(flattened))

if __name__ == '__main__':
    run()


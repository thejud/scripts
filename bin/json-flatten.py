#!/usr/bin/env python

from __future__ import print_function

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

def run():
    flattener = Flattener()
    for line in fileinput.input():
        data = json.loads(line.strip())
        print(json.dumps(flattener.flatten(data, )))

if __name__ == '__main__':
    run()


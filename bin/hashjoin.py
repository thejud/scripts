#!/usr/bin/env python
"""
NAME:

  hashjoin:

DESCRIPTION:


AUTHOR:

  Jud Dagnall <jud@dagnall.net>

EXAMPLES:

    # common usage:
    hashjoin 

"""

from __future__ import print_function

import argparse
import fileinput
import json
import logging
import re
import sys

TIMESTAMP_FORMAT='%(asctime)s %(levelname)s - %(message)s'

def parse_args(args=None):
    desc=""
    p = argparse.ArgumentParser(description=desc)
    #p.add_argument('', help="default: %(default)s", default='')
    p.add_argument('-o', '--only', action='store_true', 
        help="print only lines with matches")
    p.add_argument('lookup', help='whitespace delimited lookup')
    p.add_argument('targets', nargs='*', 
            help='targets for lookup')
  
    # accept arguments as a param, so we
    # can import and run this module with a commandline-like
    # syntax.
    if args is None: 
        args = sys.argv[1:]
    return p.parse_args(args)

def run(opts):
    logging.debug("starting")
    lookups = {}
    for line in open(opts.lookup):
        k, v = re.split(r'\s+', line.rstrip("\n"), 1)
        lookups[k] = v

    logging.debug("lookups: %s", lookups)
    for line in fileinput.input(opts.targets):
        line = line.rstrip("\n")
        matched = False
        for pattern, extra in lookups.items(): 
            if pattern in line:
                line = line + " " + extra
                matched = True
                break
        if matched or not opts.only:
            print(line)

if __name__ == '__main__':
    opts = parse_args(sys.argv[1:])
    logging.basicConfig(level=logging.INFO,format=TIMESTAMP_FORMAT)
    run(opts)

#!/usr/bin/env python
"""
NAME:

  hashjoin: join a small lookup table with unsorted targets

DESCRIPTION:

I wanted a quick way to annotate lines with additional metadata
from a lookup file.  I had a set of UUIDS and human readable
labels, and a set of target files that would be decorated by combining
the input line with the lookup value when the lookup key was present
in the line.

sample lookup: key value

id1 Item 1
id2 Another item

target:

This is id1 and other stuff
And here id2 is here


The join linux join command requires sorted input.
However, given a small lookup table hashjoin allows for
joining of unsorted lookup and target table(s).

hashjoin.py uses the first field of the lookup as the key,
and then 

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
    p.add_argument('-d', '--delimiter', 
            help="regex delimiter for lookup table",
            default='\s+')
    p.add_argument('-D', '--debug', action='store_true',
            help='enable debugging')
    p.add_argument('-o', '--only', action='store_true', 
        help="print only lines with matches")
    p.add_argument('-O', '--output-delimiter', 
                   help="output delimiter. default = space",
                   default=" ")
    p.add_argument('-T', '--tab-output', action='store_true',
                   help="use tab as the output delimiter")
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
    if opts.tab_output:
        opts.output_delimiter = "\t"

    delimiter = re.compile(opts.delimiter)

    for line in open(opts.lookup):
        k, v = re.split(delimiter, line.rstrip("\n"), 1)
        lookups[k] = v
        logging.debug('"%s" -> "%s"', k, v)

    logging.debug("lookups: %s", lookups)
    for line in fileinput.input(opts.targets):
        line = line.rstrip("\n")
        matched = False
        for pattern, extra in lookups.items():
            if pattern in line:
                line = line + opts.output_delimiter + extra
                matched = True
                logging.debug('matched %s', pattern)
                break
        if matched or not opts.only:
            print(line)

if __name__ == '__main__':
    opts = parse_args(sys.argv[1:])
    debug_level = logging.DEBUG if opts.debug else logging.INFO
    logging.basicConfig(level=debug_level ,format=TIMESTAMP_FORMAT)
    run(opts)

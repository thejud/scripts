#!/usr/bin/env python
"""
NAME:

  jset: simple set operations on unsorted input

DESCRIPTION:

    jset builds sets out of the input lines, and provides a list of lines:

        * only in the first (a - b)
        * only the second (b - a)
        * in both (a intersect b)

    There are other similar tools (like comm and zet), but jset provides
    shortcuts for visualizing and the data in tabular format, list format, json
    format and also provides some easy aliases to aid in understanding.


AUTHOR:

  Jud Dagnall <jud@dagnall.net>

EXAMPLES:

    # common usage:
    seq 1 10 > a
    seq 6 4 > b
    echo 99 >> b

    jset.py a b

    jset.py -T a b

    jset -1  a b

"""

from __future__ import print_function

import argparse
import json
import logging
import sys

TIMESTAMP_FORMAT='%(asctime)s %(levelname)s - %(message)s'

def parse_args(args=None):
    desc="set difference and intersection"
    p = argparse.ArgumentParser(description=desc)
    #p.add_argument('', help="default: %(default)s", default='')
    p.add_argument('-1', '--first', '--only-first', action='store_true')
    p.add_argument('-2', '--second', '--only-second', action='store_true')
    p.add_argument('-3', '-x', '--both', '--intersect', action='store_true')
    p.add_argument('-j', '--json', action='store_true')
    p.add_argument('-T', '--table', action='store_true', help="tabulate format")
    p.add_argument('a', type=argparse.FileType('r'))
    p.add_argument('b', type=argparse.FileType('r'))
  
    # accept arguments as a param, so we
    # can import and run this module with a commandline-like
    # syntax.
    if args is None: 
        args = sys.argv[1:]
    return p.parse_args(args)

def print_join(data):
    if not data:
        return
    for item in data:
        print(item)

def print_table(out):
    from tabulate import tabulate
    lines = make_matrix(out)

    print(tabulate(lines, headers=['only_a', 'only_b', 'both']))

def make_matrix(out):
    both = set(out['both'])
    a = set(out['only_a'])
    b = set(out['only_b'])

    lines = []
    for item in sorted(a.union(b).union(both)):
        row = [""] * 3
        if item in both: 
            row[2] = item
        elif item in a:
            row[0] = item
        else:
            row[1] = item      
        lines.append(row)
    return lines

def run(opts):
    logging.debug("starting")
    a = set([line.rstrip("\n") for line in opts.a])
    b = set([line.rstrip("\n") for line in opts.b])

    out = {
            'only_a': sorted(list(a - b)),
            'only_b':  sorted(list(b - a)),
            'both': sorted(list(a.intersection(b))),
    }

    if opts.first:
        print_join(out['only_a'])
    elif opts.second:
        print_join(out['only_b'])
    elif opts.both:
        print_join(out['both'])
    elif opts.json:
        print(json.dumps(out, indent=2))
    elif opts.table:
        print_table(out)
    else:
        for section in ['only_a', 'only_b', 'both']:
            fname = ""
            if section == 'only_a': fname = opts.a.name 
            elif section == 'only_b': fname = opts.b.name 
            print(f"{'-'*10} {section} {fname} {'-'*10}")
            print_join(out[section])


if __name__ == '__main__':
    opts = parse_args(sys.argv[1:])
    logging.basicConfig(level=logging.INFO,format=TIMESTAMP_FORMAT)
    run(opts)

#!/usr/bin/env python3
"""
NAME:

  parse-kv-csv.py: Parse comma-separated lists of kv pairs

DESCRIPTION:

    Simple parser for comma-separated pairs of k=v data, e.g.
    field1=foo,field2="some,string",field2="some words"


AUTHOR:

  Jud Dagnall <git@dagnall.net>

EXAMPLES:

    # common usage:
    echo 'f1=2,f2="testing"' | parse-kv-csv.py
    {"f1":2, "f2":testing}

BUGS:

    strings with commas in them are not parsed correctly.


"""

from __future__ import print_function

import argparse
import json
import logging
import sys
import csv

LOG_FORMAT='%(asctime)s %(levelname)s - %(message)s'


def parse_args(args=None):
    desc=""
    p = argparse.ArgumentParser(description=desc)
    p.add_argument('-d', '--debug', action='store_true', 
    help='enable debug output')
    p.add_argument('files', nargs='*', type=argparse.FileType('r'),
            default=[sys.stdin],
            help="input file(s) or stdin")
    #p.add_argument('', help="default: %(default)s", default='')
  
    # accept arguments as a param, so we
    # can import and run this module with a commandline-like
    # syntax.
    if args is None: 
        args = sys.argv[1:]
    return p.parse_args(args)


def run(opts):
    logging.debug("starting")
    if opts.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    for fh in opts.files:
        for line in fh:
            line=line.strip()
            logging.debug("line=%s", line)
            event = {}
            fields = list(csv.reader([line]))[0]
            logging.debug("fields=%s", fields)
            for field in fields:
                logging.debug(f"field={field}")
                k, v = field.split("=", 1)
                k=k.strip()
                v = v.rstrip('"').lstrip('"')
                logging.debug(f"k={k} v={v}")
                event[k] = v
            print(json.dumps(event))

if __name__ == '__main__':
    opts = parse_args(sys.argv[1:])
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    run(opts)

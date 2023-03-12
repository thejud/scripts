#!/usr/bin/env python
"""
NAME:

  join-to-csv:

DESCRIPTION:


AUTHOR:

  Jud Dagnall <jdagnall@splunk.com>

EXAMPLES:

    # common usage:
    join-to-csv 

"""

from __future__ import print_function

import argparse
import fileinput
import json
import logging
import sys

TIMESTAMP_FORMAT='%(asctime)s %(levelname)s - %(message)s'

def parse_args(args=None):
    desc=""
    p = argparse.ArgumentParser(description=desc)
    #p.add_argument('', help="default: %(default)s", default='')
    p.add_argument('-q', '--quote', help="quote character, default: %(default)s", default='"')
  
    p.add_argument('files', nargs='*', help="read from one or more files. default is stdin")
  
    # accept arguments as a param, so we
    # can import and run this module with a commandline-like
    # syntax.
    if args is None: 
        args = sys.argv[1:]
    return p.parse_args(args)

def run(opts):
    logging.debug("starting")
    print(",".join([ opts.quote + s.strip() + opts.quote for s in
        fileinput.input(opts.files) ]))


if __name__ == '__main__':
    opts = parse_args(sys.argv[1:])
    logging.basicConfig(level=logging.DEBUG,format=TIMESTAMP_FORMAT)
    run(opts)

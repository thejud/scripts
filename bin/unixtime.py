#!/usr/bin/env python
"""
NAME:

  unixtime: convert to/from unixt timestamps

DESCRIPTION:


AUTHOR:

  Jud Dagnall <jdagnall@splunk.com>

EXAMPLES:

    # common usage:
    unixtime 

"""

from __future__ import print_function

from datetime import datetime

import argparse
import logging
import re
import sys
import time

TIMESTAMP_FORMAT='%(asctime)s %(levelname)s - %(message)s'


class UnixTimeParser:
    def __init__(self, utc_output=False, int_output=True):
        self.utc_output = utc_output
        pass

    def format_datetime(self, epoch):
        if self.utc_output:
            timestamp = time.localtime(float(epoch))
            st = time.strftime('%Y-%m-%d %H:%M:%S.%f', epoch)[:-3]
            return st + time.strftime(' %z')
        else:
            timestamp = time.gmtime(float(epoch))
            st = time.strftime('%Y-%m-%d %H:%M:%S.%f', epoch)[:-3]
            return st + " UTC"
        return 

    def parse_digits(self, chars):
        if len(chars) > 10:
            epoch = self.parse_java(chars)
        else:
            epoch = self.parse_unix(chars)
        return self.format_datetime(epoch)

    def parse_unix(self, line):
        return int(line)

    def parse_java(self, line):
        return int(line)/1000

def parse_args(args=None):
    desc="generate, parse and convert to/from unix-style timestamps"
    p = argparse.ArgumentParser(description=desc)
    #p.add_argument('', help="default: %(default)s", default='')
  
    # accept arguments as a param, so we
    # can import and run this module with a commandline-like
    # syntax.
    if args is None: 
        args = sys.argv[1:]
    return p.parse_args(args)

def run(opts):
    logging.debug("starting")
    if opts.args == [] and not opts.filter:
        print(int(time.time()))

    parser = UnixTimeParser()
    if opts.args:
        for line in opts.args:
            print(parser.parse(item))

if __name__ == '__main__':
    opts = parse_args(sys.argv[1:])
    logging.basicConfig(level=logging.DEBUG,format=TIMESTAMP_FORMAT)
    run(opts)

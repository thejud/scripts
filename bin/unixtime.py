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

import pytz
import tzlocal


TIMESTAMP_FORMAT='%(asctime)s %(levelname)s - %(message)s'

OFFSET=1
UTC=2
LOCALIZED=3

class LocalizeConverter:
    def convert_to_datetime(self, epoch, tz_format):
        localzone = tzlocal.get_localzone()
        timestamp = datetime.fromtimestamp(epoch, pytz.utc)
        localtime = timestamp.replace(tzinfo=pytz.utc).astimezone(localzone)
        return localtime.strftime(tz_format + ' %z')

class UtcConverter:
    def convert_to_datetime(self, epoch, tz_format):
        timestamp = datetime.utcfromtimestamp(epoch)
        return timestamp.strftime(tz_format) + 'Z'

class OffsetConverter:
    def convert_to_datetime(self, epoch, tz_format):
        timestamp = datetime.fromtimestamp(epoch)
        return timestamp.strftime(tz_format) + time.strftime(" %z")

class UnixTimeParser:
    def __init__(self, tz_output=OFFSET, int_output=True):
        self.tz_output = tz_output
        self.tz_format= '%Y-%m-%d %H:%M:%S'
        if tz_output==LOCALIZED:
            self.converter = LocalizeConverter()
        elif tz_output==UTC:
            self.converter = UtcConverter()
        else:
            self.converter = OffsetConverter()


    def format_datetime(self, epoch):
        return self.converter.convert_to_datetime(epoch, self.tz_format)


    def parse_digits(self, chars):
        if len(chars) > 10:
            epoch = self.parse_java(chars)
        else:
            epoch = self.parse_unix(chars)
        return self.format_datetime(epoch)

    def parse_unix(self, chars):
        return int(chars)

    def parse_java(self, chars):
        return int(chars)/1000

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

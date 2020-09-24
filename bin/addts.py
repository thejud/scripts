#!/usr/bin/env python
"""add timestamp prefix to input
"""

from __future__ import print_function

import argparse
import fileinput
import sys
from datetime import datetime

parser = argparse.ArgumentParser("prefix each line with a timestamp")
parser.add_argument("--format", "-f", 
    help="strftime fromrmat string. default=%(s)", 
    default="%Y-%m-%dT%H:%M:%S ")
parser.add_argument("files", default="-", nargs="*", help="input file(s). Default: stdin")
opts=parser.parse_args()

for line in fileinput.input(opts.files):
    print(datetime.now().strftime(opts.format), end="")
    print(line, end="", flush=True)

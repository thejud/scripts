#!/usr/bin/env python
"""
convert yaml data to json
"""

from __future__ import print_function
import json
import fileinput
import yaml
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--compact', '-c', action='store_true', help='enable compact mode')
parser.add_argument('files', nargs='*')
args = parser.parse_args()

indent = None if args.compact else 2

yaml_data = "".join([line for line in fileinput.input(args.files)])
print(json.dumps(yaml.safe_load(yaml_data), sort_keys=True, indent=indent))


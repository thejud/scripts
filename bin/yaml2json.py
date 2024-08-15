#!/usr/bin/env python
"""
convert yaml data to json
"""

from __future__ import print_function
import argparse
import fileinput
import json
import pprint
import sys
import yaml

parser = argparse.ArgumentParser()
parser.add_argument('--compact', '-c', action='store_true', help='enable compact mode')
parser.add_argument('--debug', '-d', action='store_true', help='enable debugging')
parser.add_argument('files', nargs='*')
args = parser.parse_args()

indent = None if args.compact else 2

# disable auto-parsing of dates - https://stackoverflow.com/a/52312810
yaml.SafeLoader.yaml_implicit_resolvers = {
    k: [r for r in v if r[0] != 'tag:yaml.org,2002:timestamp'] for
    k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()
}

yaml_data = "".join([line for line in fileinput.input(args.files)])
data = yaml.safe_load(yaml_data)
if args.debug:
    pprint.pprint(data, stream=sys.stderr)
print(json.dumps(data, sort_keys=True, indent=indent))


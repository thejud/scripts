#!/usr/bin/env python
"""
convert yaml data to json
"""

from __future__ import print_function
import json
import fileinput
import yaml

yaml_data = "".join([line for line in fileinput.input()])
print(json.dumps(yaml.load(yaml_data), sort_keys=True, indent=2))


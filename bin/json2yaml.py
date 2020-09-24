#!/usr/bin/env python
"""
convert yaml data to json
"""

from __future__ import print_function
import json
import fileinput
import yaml

json_data = "".join([line for line in fileinput.input()])
print(yaml.safe_dump(json.loads(json_data)))


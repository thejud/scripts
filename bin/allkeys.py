#!/usr/bin/env python3
"""print unique keys in a series of jsonl objects, in the order they appear

EXAMPLES:
    printf '{"b":1,"a":2}\n{"b":2,"c":3}' | allkeys.py
    b
    a
    c

    allkeys.py f1.jsonl f2.jsonl

"""

import json
import fileinput

keys = set()
for line in fileinput.input():
    for key in json.loads(line).keys():
        if key not in keys:
            print(key)
            keys.add(key)



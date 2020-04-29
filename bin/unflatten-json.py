#!/usr/bin/env python3
"""Convert json with a flat keyspace into a hierarchy

e.g. {"a.b.c": 2}  into {"a": {"b": {"c": 2}}}

"""

import fileinput
import json

def unflatten(data, sep="."):
    out = dict()
    for key,value in data.items():
        parts = key.split(sep)
        if len(parts) == 1:
            out[key] = value
        else:
            current = out
            for child in parts[0:-1]:
                if child not in current:
                    current[child] = dict()
                current = current[child]
            current[parts[-1]] = value
    print(json.dumps(out, sort_keys=True))

for line in fileinput.input():
    unflatten(json.loads(line.rstrip()))


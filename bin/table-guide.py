#!/usr/bin/env python
"""
some table-formatting foo to support condensed output
for visidata guides:

For example,

date        sum_R  avg_R  sum_B  avg_B
----------  -----  -----  -----  -----
2024-09-01  30     30     0
2024-09-02  0             28     28
2024-09-03  100    100    132    66


Auto-detects tabs, commas and falls back to space-separated.

"""

import fileinput
import re

from tabulate import tabulate

lines = [line.strip() for line in fileinput.input()]

if "\t" in lines[0]:
    separator = re.compile("\t")
elif "," in lines[0]:
    separator = re.compile(",")
else:
    separator = re.compile(r"\s+")

fields = [separator.split(line) for line in lines]
out = tabulate(
    fields, colalign=("left",), tablefmt="simple", disable_numparse=True
).split("\n")
out[0], out[1] = out[1], out[0]
out.pop()

print("\n".join(out))

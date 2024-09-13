#!/usr/bin/env python
"""
Parse fixed-width table output from a spark datafram dump

+----------+---------+----------+----------+-------+
|day       |dayOfWeek|week      |weekend   |holiday|
+----------+---------+----------+----------+-------+
|2023-05-25|Thu      |2023-05-22|NULL      |NULL   |
+----------+---------+----------+----------+-------+

becomes

{"day": "2023-05-25", "dayOfWeek": "Thu", "week": "2023-05-22", "weekend": "NULL", "holiday": "NULL"}


Note that you can use mlr --n2x to get a nice long output version

See also: untabulate.py

"""

import fileinput
import json
import logging
import re
import sys
import tabulate
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Parse fixed-width columns to JSON")
    parser.add_argument('input_file', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
                        help="Input file containing fixed-width formatted data. Defaults to STDIN if not provided.")
    parser.add_argument('-t', '--table', action='store_true',
                        help="output data in long table format instead of json")
    return parser.parse_args()

def split_fixed(line, ranges, rstrip=True, lstrip=False):
    fields = []
    for (start, end) in ranges:
        field = line[start:end]
        if rstrip:
            field = field.rstrip()
        if lstrip:
            field = field.lstrip()
        fields.append(field)
    return fields


def main(opts):
    lines = [line.strip() for line in opts.input_file if not line.startswith('+-')]

    header = lines[0]
    column_names = [name.strip() for name in header.split('|')]

    # remove the empty first column from the initial '|'
    column_names = column_names[1:]

    # Find all positions of the '|' character
    positions = [match.start() for match in re.finditer(r'\|', header)]

    # Create the ranges by pairing the positions
    logging.debug("headers: %s", column_names)

    ranges = [(positions[i] + 1, positions[i + 1]) for i in range(len(positions) - 1)]
    logging.debug("ranges: %s", ranges)

    parsed = [split_fixed(line, ranges) for line in lines[1:]]
    kv = [dict(zip(column_names, fields)) for fields in parsed]

    if opts.table:
        logger.error("tables not supported yet. Use mlr --n2x")
        sys.exit(1)

    ## JSON output
    for row in kv:
        print(json.dumps(row))

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    opts = parse_args()
    main(opts)


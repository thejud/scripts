#!/usr/bin/env python
"""
NAME:

  lookupfilter: lookup and replace multiple kv pairs

DESCRIPTION:

    Lookup and replace multiple strings in the input
    given a set of pattern -> replacement pairs
    in a tab-separated lookup file.


AUTHOR:

  Jud Dagnall <github@dagnall.net>

EXAMPLES:

    # common usage: replace all ip addresses with their hostnames
    cat log | lookupfilter --lookup ip2host.tsv

"""

from __future__ import print_function

import argparse
import fileinput
import logging
import sys

TIMESTAMP_FORMAT = "%(asctime)s %(levelname)s - %(message)s"


def parse_args(args=None) -> argparse.Namespace:
    desc = "lookup and replace multiple kv pairs"
    p = argparse.ArgumentParser(description=desc)
    # p.add_argument('', help="default: %(default)s", default='')
    p.add_argument(
        "-d",
        "--delimiter",
        default="\t",
        help="delimiter for lookup file. Default: %(default)s",
    )
    p.add_argument(
        "-l", "--lookup", required=True, help="tab-separated lookup table k->v"
    )
    p.add_argument("input", nargs="*", help="input files to filter. Default: stdin")

    # accept arguments as a param, so we
    # can import and run this module with a commandline-like
    # syntax.
    if args is None:
        args = sys.argv[1:]
    return p.parse_args(args)


def load_lookups(opts: argparse.Namespace) -> dict[str, str]:
    lookups = {}
    delimiter = opts.delimiter or "\t"
    logging.info(f"reading lookups: {opts.lookup}")
    with open(opts.lookup, "r") as fh:
        for line in fh:
            k, v = line.rstrip().split(delimiter, 2)
            lookups[k] = v
    logging.debug(f"lookup count: {len(lookups.keys())}")
    return lookups


def replace_lines(opts: argparse.Namespace, lookups: dict[str, str]):
    for line in fileinput.input(opts.input):
        for k, v in lookups.items():
            if k in line:
                line = line.replace(k, v)
        yield line


def run(opts: argparse.Namespace):
    logging.debug("starting")
    lookups = load_lookups(opts)
    for line in replace_lines(opts, lookups):
        print(line, end="")


if __name__ == "__main__":
    opts = parse_args(sys.argv[1:])
    logging.basicConfig(level=logging.DEBUG, format=TIMESTAMP_FORMAT)
    run(opts)

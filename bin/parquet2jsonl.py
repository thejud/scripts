#!/usr/bin/env python

import pandas as pd

import argparse
import logging
import sys

p = argparse.ArgumentParser("quick parquet 2 json converter")
p.add_argument("files", nargs="+", help="parquet files to convert")
opts, args = p.parse_known_args()

logging.basicConfig(level=logging.DEBUG)


for f in opts.files:
    logging.debug("parquet_file: %s", f)
    df = pd.read_parquet(f)
    df.to_json(sys.stdout, orient="records", lines=True)

#!/usr/bin/env python
"""
reformats AND OVEWRITES one or more files using the json pretty printer


EXAMPLES

# dry run (the default). Checks that all files can be parsed
pretty_reprint.py *.json

# reformat all json files in a directory, overwriting the originals
pretty_reprint.py --overwrite *.json



"""

import sys
import json
import logging
import argparse
import pathlib

logging.basicConfig(level=logging.DEBUG)

def process_file(file_path, overwrite=False):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

        if overwrite:
            output_file_path = file_path

            with open(output_file_path, 'w') as output_file:
                json.dump(data, output_file, indent=4)

            logging.info(f'File "{file_path}" parsed and pretty-printed to "{output_file_path}"')
        else:
            logging.info(f'File "{file_path}" parsed (dry-run mode)')

    except (json.JSONDecodeError, FileNotFoundError) as e:
        logging.error(f'Error parsing file "{file_path}": {str(e)}')

# Create the command line argument parser
parser = argparse.ArgumentParser()
parser.add_argument('--overwrite', action='store_true', help='overwrite the input files. Otherwise they will just be checked')
parser.add_argument('files', nargs='+', help='Input files to process. '-' to read from stdin')

# Parse the command line arguments
args = parser.parse_args()

# Iterate over the input files and process them accordingly
for path in args.files:
    if path == "-":
        for filename in sys.stdin:
            process_file(filename.strip(), overwrite=args.overwrite)
    else:
        process_file(path, overwrite=args.overwrite)


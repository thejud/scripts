#!/usr/bin/env python3
"""
Convert pretty-printed tabular data back into
CSV, and/or to some convenient output formats.


spark dataframe.show(), psql and other tools sometimes
output data in tabular format. It is useful for interactive debugging, but
sometimes the dataframes get much to wide to view comfortable. 

Untabulate provides the option to parse to CSV, and then to output as either a
'transposed' format, a long format where each input row as printed separately
the long way, or standard CSV so you can roll your own.


Sample input:

+------+----------+-----------------+
| date |   name   |     address     |
+------+----------+-----------------+
| 2014 |   Jud    | 217 main Street |
| 1492 | Columbus |     America     |
+------+----------+-----------------+


### CSV output

$ untabulate.py sample.txt
date,name,address
2014,Jud,217 main Street
1492,Columbus,America

### transposed output

$ untabulate.py -t sample.txt
fieldname,1,2
date,2014,1492
name,Jud,Columbus
address,217 main Street,America


### transposed and pretty printed output


$ untabulate.py -tp /tmp/sample.txt
fieldname    1                2
-----------  ---------------  --------
date         2014             1492
name         Jud              Columbus
address      217 main Street  America


### long format output

 $ untabulate.py -l /tmp/sample.txt
-------  ---------------
date     2014
name     Jud
address  217 main Street
-------  ---------------

-------  --------
date     1492
name     Columbus
address  America
-------  --------1



"""

from collections import OrderedDict
from pathlib import Path

import argparse
import csv
import fileinput
import logging
import sys
import tabulate

def parse_table(input_lines):
    lines = list(input_lines)

    # Determine column widths
    col_widths = [len(x) for x in lines[0].split('+')[1:-1]]

    # Extract column names
    col_names = lines[1].split('|')[1:-1]
    col_names = [x.strip() for x in col_names]
    logging.debug("names: %s", col_names)
    logging.debug("withs: %s", col_widths)

    # Parse the data
    data = [col_names]
    for line in lines[3:]:
        if line.startswith('+'):
            continue

        start = 1
        row = []
        for width, col_name in zip(col_widths, col_names):
            row.append(line[start:start+width].strip())
            start += width + 1
        data.append(row)

    return col_names, data

def write_csv(data):
    writer = csv.writer(sys.stdout)
    writer.writerows(data)

def write_pretty(data, print_format, header=True, outfile=sys.stdout):
    print(tabulate.tabulate(data, headers="firstrow" if header else [],
                            tablefmt=print_format,
                            numalign=None,
                            disable_numparse=True,
                            ), file=outfile)

def add_row_numbers(rows, column_name='rownum'):
    yield [column_name, *rows[0]]

    for i, row in enumerate(rows[1:]):
        yield [i+1, *row]

def transpose(data):
    return zip(*add_row_numbers(data, 'fieldname'))

def write_long(data, print_format, outfile=sys.stdout):
    headers = data[0]

    for row in data[1:]:
        transposed = list(transpose([headers, row]))
        write_pretty(transposed[1:], print_format, header=False, outfile=outfile)
        print(file=outfile)

def write_long_files(data, print_format, folder):
    headers = data[0]
    for i, row in enumerate(data[1:]):
        outfile = Path(folder)/str(i+1).zfill(2)
        transposed = list(transpose([headers, row]))
        with open(outfile, 'w') as handle:
            write_pretty(transposed[1:], print_format, header=False, outfile=handle)
            logging.info("wrote %s", outfile)


def run(opts):
    logging.debug("starting")
    col_names, data = parse_table(fileinput.input(opts.files))
    if opts.transpose:
        data = transpose(data)
    if opts.pretty:
        write_pretty(data, opts.format)
    elif opts.long:
        write_long(data, opts.format)
    elif opts.long_files:
        write_long_files(data, opts.format, opts.long_files)
    else:
        write_csv(data)


def parse_args():
    parser = argparse.ArgumentParser(description='Parse tabular data.')
    parser.add_argument('-d', '--debug', action='store_true', help='turn on debugging')
    parser.add_argument('-t', '--transpose', action='store_true', help='Transpose the output CSV')
    parser.add_argument('-p', '--pretty', action='store_true', help='pretty print the output')
    parser.add_argument('-l', '--long', action='store_true', help='long format. Also uses prety printing')
    parser.add_argument('-L', '--long-files', help='write each row to a numbered output file in <folder>for diffing')
    parser.add_argument('-f', '--format', help='tabulate format for output.' +
                        'Default is %(default). options include grid, psql, markdown',
                        default='simple')
    parser.add_argument('files', nargs='*', help='input file(s). Otherwise STDIN is used')
    return parser.parse_args()

if __name__ == "__main__":
    opts = parse_args()
    logging.basicConfig(level=logging.DEBUG if opts.debug else logging.INFO)

    run(opts)

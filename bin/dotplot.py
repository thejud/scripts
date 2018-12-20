#!/usr/bin/env python
"""
NAME:

  dotplot: quick single variable visualization

DESCRIPTION:

    Every wanted to quickly visualize some log output from the command line?
    I often grab some data out of a logfile, and then want to visualize it, e.g.
    What is the hourly rate of this error message.
    Input is two columns. Unless --basic is specified, the first column is a
    datetime, and the second column is a value. --basic turns on the basic 
    x.y plot mode, where the first column is just x, and the second column is y.

AUTHOR:

  Jud Dagnall <jud@dagnall.net>

REQUIREMENTS:

    The python pandas and matplot libraries are required.

EXAMPLES:

    # common usage:



from python:

    import dateplot
    opts = dateplot.parse_args(['/tmp/mydata'])

    # dateplot.run(opts)
    df = dateplot.get_data(opts)
    dateplot.plot(df, opts)

There are a lot of options so that it can be quickly used for a variety of stuff.

"""

from __future__ import print_function

import argparse
import fileinput
import logging
import os
import sys

from pandas import Series, DataFrame
import pandas
import matplotlib.pyplot

pd = pandas
plt = matplotlib.pyplot

cf0 = '{:,.0f}'.format
cf2 = '{:,.2f}'.format


TIMESTAMP_FORMAT='%(asctime)s %(levelname)s - %(message)s'

def parse_args(args=None):
    desc=""
    p = argparse.ArgumentParser(description=desc)
    p.add_argument('--outfile', '-o', 
        help='output file. default=%(default)s',
        default='/tmp/dateplot.png')
    p.add_argument('--symbol', '-s', 
            help='alternate symbol, e.g. "*" for chart')
    p.add_argument('--title', '-T', 
            help="title for the chart")

    p.add_argument('-x', type=float, help='chart width (inches)')
    p.add_argument('-y', type=float, help='chart height (inches)')
    p.add_argument('--large', '-L', action='store_true',
            help='large output dimensions, 10x12',)

    p.add_argument('--points', '-p', 
        help='matplotlib point format string., e.g. "." or "xb-" default=%s(default)',
        default='o')

    p.add_argument('input', nargs='*',
        help='zero or more input files. Otherwise read from STDIN',)
  
    # accept arguments as a param, so we
    # can import and run this module with a commandline-like
    # syntax.
    if args is None: 
        args = sys.argv[1:]
    return p.parse_args(args)

def get_data(opts):
    args = {
    'names':['val'],
    }
    if opts.tsv:
         args['sep'] = '\t'
        
    elif opts.csv:
         args['sep'] = ','
    else:
        args['sep'] = r"\s+"
    
    indata = pd.compat.StringIO("".join([s for s in fileinput.input(opts.input)]))
    df = pd.read_table(indata, **args)

    logging.debug(df.head())
    logging.debug("dtype: %s", df.dtypes)

    #df = df.sort_values('datetime', ascending=True)
    return df

def plot(df, opts):

    dims = [6,4]
    if opts.large:
        dims = [20,10]
    if opts.x:
        dims[0] = opts.x
    if opts.y:
        dims[1] = opts.y

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(opts.points,y=df['val'])
    date_format = get_date_output(opts)

    if opts.title:
        plt.title(opts.title)

    fig.set_size_inches(*dims)
    plt.savefig(opts.outfile)

def run(opts):
    logging.debug("starting")
    df = get_data(opts)
    plot(df, opts)

    cmd = ['open', opts.outfile]
    logging.info(cmd)
    os.execvp(cmd[0], cmd)

if __name__ == '__main__':
    opts = parse_args(sys.argv[1:])
    logging.basicConfig(level=logging.DEBUG,format=TIMESTAMP_FORMAT)
    run(opts)

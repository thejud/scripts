#!/usr/bin/env python
"""
NAME:

  dateplot: quickly plot some timeseries data

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

    # quickly plots some timetamped data
    cat <<EOF | dateplot.py
    2018-01-02T12:04:01 99
    2018-01-02T12:05:01 22
    2018-01-03T12:04:01 192
    2018-01-04T12:22:51 300
    EOF

    # quickly plot any x,y data
    # perl generates 1000 random y values
    # use nl to give sequential x values for a set of y values
    # NOTE: skip nl if your data has both x and y values.
    perl -E'say(rand()) for 1..1000' | nl | dateplot.py --basic --large

    # grab logfile data, and plot error counts per minute
    # the initial perl regular expression extracts the timestamp at minute
    # resolution (by excluding the seconds), aggregates and counts the
    # occurrence of each minute. awk is used to reverse the order of the
    # columns, so that each line is "<minute> <count>"

    cat logfile  \
        | grep ERROR \
        | perl -nE'/(2018-\d\d-\d\dT\d\d:\d\d):\d\d/ and say $1' \
        | sort | uniq -c \
        | awk '{print $2,$1}' \
        dateplot.py --minute --large

Date/Time parsing:
    A few date+time formats are understood 
    YYYY-MM-DDTHH:MM:SS
    YYYY-MM-DD
    YYYY-MM-DDT:HH
    HH:MM:SS (today)
    HH:MM  (today)


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
    p.add_argument('--csv', '-c', action='store_true',
        help='input is CSV. Otherwise, whitespace is assumed'
        )
    p.add_argument('--tsv', '--tabs','-t', action='store_true',
        help='input is tab separated. Otherwise, whitespace is assumed'
        )
    p.add_argument('--month', '-m', action='store_true',
        help='output date with month precision')
    p.add_argument('--day', '-d', action='store_true',
        help='output date with day precision')
    p.add_argument('--hour', '-H', action='store_true',
        help='output date with hour precision. This is the default')
    p.add_argument('--minute', '-M', action='store_true',
        help='output date with minute precision.')
    p.add_argument('--output-date-format', '-D',
        help='strftime string for date output, e.g. "%%Y-%%m-%%dT%%H"')
    p.add_argument('--rotation', '-r', type=float,
        help='rotation angle for date output. Default=%(default)s',
        default=30,)
    p.add_argument('--basic', '-b', action='store_true',
            help='basic plot. First column is not a datetime')

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
        default='-')

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
    'names':['datetime', 'val'],
    }
    if not opts.basic:
        args['parse_dates']=['datetime']

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

def get_date_output(opts):
    if opts.day:
        fmt = '%Y-%m-%d'
    elif opts.month:
        fmt = '%Y-%m'
    elif opts.hour:
        fmt = '%Y-%m-%d %H'
    elif opts.minute:
        fmt = '%Y-%m-%d %H:%M'
    elif opts.output_date_format:
        fmt = opts.output_date_format
    else:
        fmt = '%Y-%m-%d %H'
    return fmt


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
    ax.plot(df['datetime'], df['val'], opts.points)
    date_format = get_date_output(opts)

    if not opts.basic:
        import matplotlib.dates as mdates
        ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
        # rotate and align the tick labels so they look better
        fig.autofmt_xdate(rotation=opts.rotation, bottom=0.3)

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

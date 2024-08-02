#!/usr/bin/env python
"""
Quantize input timestamps into buckets, e.g. daily or 4 hour blocks

Often when processing log data on the command line, it is useful to aggregate it into buckets
for further processing. `quantize_times.py` allows for complex bucketing that can account for
various time formats, and specific bucket sizes.

It will auto-parse several common formats, including:
    - ISO 8601 format (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
    - Common US format (MM/DD/YYYY or MM/DD/YYYY HH:MM:SS AM/PM)
    - Common European format (DD/MM/YYYY or DD/MM/YYYY HH:MM:SS)
see pandas.to_datetime for the gory details

use --date-format to provide a custom date parsing string. See the python strptime model for the format codes.

use the --unix-timestamp flag to parse unix (second) and/or java (milliseconds) epoch times.


Examples:

    Given input like time.txt:
        08/01/2024 07:08:30 AM
        08/01/2024 12:25:08 AM
        08/01/2024 03:08:57 AM

    # Quantize times into default 4 hour buckets
    cat times.txt | quantize_times.py
    2024-08-01 04:00:00
    2024-08-01 00:00:00
    2024-08-01 00:00:00

    # 30 minute buckets
    quantize_times.py -b 30min

    # handle unix timestamps. Will auto-detect seconds vs. milliseconds
    printf "1722633512\n1722633520000" | quantize_times.py -b 10s -u
    2024-08-02 21:18:30
    2024-08-02 21:18:40


    # custom time format.

    printf "2024+12+13" | quantize_times.py -d '%Y+%m+%d'
    2024-12-13 00:00:00


## Limitations

No handling of timezones is provided.


## TODO

- provide custom output string format

"""

import pandas as pd

import argparse
import fileinput


def parse_args():
    parser = argparse.ArgumentParser(description="Quantize date/time stamps to specified bucket size.")
    parser.add_argument("--bucket_size", "-b", type=str, default='4H',
                        help="The size of the time bucket (e.g., '4H', '2D','30min'). default: %(default)s")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--date-format', '-d', type=str,
                       help='Custom date format for parsing ' +
                            ' (e.g., "%%m/%%d/%%Y %%I:%%M:%%S %%p").')
    group.add_argument('--unix-timestamp', '-u', action='store_true',
                       help='Indicate that the input dates are Unix timestamps.')
    parser.add_argument('files', nargs='*', help='Files to read from (if empty, stdin is used).')

    return parser.parse_args()


def quantize_datetime(date_str, bucket_size, date_format=None, unix_timestamp=False):
    if unix_timestamp:
        # Check if the timestamp is in seconds (10 digits) or milliseconds (13 digits)
        timestamp_length = len(date_str)
        if 8 <= timestamp_length <= 12:
            date = pd.to_datetime(int(date_str), unit='s')
        elif 12 < timestamp_length <= 15:
            date = pd.to_datetime(int(date_str), unit='ms')
        else:
            raise ValueError(f"Invalid Unix timestamp length. Should be 8-14 digits: {date_str}")
    else:
        if date_format:
            date = pd.to_datetime(date_str, format=date_format)
        else:
            date = pd.to_datetime(date_str)
    return date.floor(bucket_size)


def run(opts):
    for line in fileinput.input(opts.files):
        quantized_date = quantize_datetime(line,
                                           bucket_size=opts.bucket_size,
                                           date_format=opts.date_format,
                                           unix_timestamp=opts.unix_timestamp)
        print(quantized_date)


if __name__ == '__main__':
    opts = parse_args()
    run(opts)

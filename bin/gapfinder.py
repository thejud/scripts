#!/usr/bin/env python3
"""
find gaps in logfiles
"""

import argparse
import datetime
import re
import sys

def identify_gaps(logfile, output_file, gap_threshold, context):
    pattern = re.compile(r'^\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\s+')

    lines = [line.rstrip('\n') for line in logfile]
    num_lines = len(lines)

    # Keep track of the last matching line index
    last_match_index = -1

    for i in range(num_lines):
        if not pattern.match(lines[i]):
            continue

        curr_time = datetime.datetime.strptime(pattern.match(lines[i]).group(), '%y/%m/%d %H:%M:%S ')

        if last_match_index >= 0:
            time_diff = (curr_time - prev_time).total_seconds()

            if time_diff > gap_threshold:
                output_file.write(f"\nGap detected: {time_diff} seconds between the following lines:\n")

                # Print context lines before the gap
                start_index = max(0, last_match_index - context)
                for j in range(start_index, last_match_index):
                    output_file.write(lines[j] + '\n')

                output_file.write(lines[last_match_index] + '\n')
                output_file.write(f"===== GAP =====\n")
                output_file.write(lines[i] + '\n')

                # Print context lines after the gap
                end_index = min(num_lines, i + context + 1)
                for j in range(i+1, end_index):
                    output_file.write(lines[j] + '\n')

        prev_time = curr_time
        last_match_index = i

if __name__ == '__main__':
    default_logfile = 'stdin'
    default_output_file = 'stdout'
    default_gap_threshold = 5
    default_context = 1

    parser = argparse.ArgumentParser(description='Identify gaps in logfiles.')
    parser.add_argument('--logfile', '-l', type=argparse.FileType('r'), default=sys.stdin,
                        help=f'input logfile name (default: {default_logfile})')
    parser.add_argument('--output_file', '-o', type=argparse.FileType('w'), default=sys.stdout,
                        help=f'output filename (default: {default_output_file})')
    parser.add_argument('--gap_threshold', '-g', type=int, default=default_gap_threshold,
                        help=f'gap threshold in seconds (default: {default_gap_threshold})')
    parser.add_argument('--context', '-c', type=int, default=default_context,
                        help=f'number of context lines to print (default: {default_context})')
    args = parser.parse_args()

    identify_gaps(args.logfile, args.output_file, args.gap_threshold, args.context)

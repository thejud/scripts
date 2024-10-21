#!/usr/bin/env python3

"""
This script prints the first and last N lines of one or more input files, or from stdin if no files are provided.
It takes optional command-line arguments to customize the number of lines printed, the display of headers, and printing a separator.

Command-line arguments:
  -n, --linecount <int> : Number of lines to print at the beginning and end of each file (default: 5)
  -H, --no-header       : Suppress printing the header between files
  -s, --separator       : Print a separator ("...") between the head and tail of each file
  files                 : Files to process. If none provided, read from stdin.

Behavior:
  - If only one input file is provided or input is read from stdin, the header will not be printed.
  - If more than one input file is provided and the -H/--no-header option is not set, a header containing the filename will be printed before printing the lines for each file.
  - If there are not enough lines to print 'linecount' lines of head and tail in a file, only as many lines as are available will be printed, without repeating any lines.
  - If the last line of output for a given input does not end with a newline, a newline character will be added.

Example usage:
  ./head_tail.py -n 1 file1.txt file2.txt
  ./head_tail.py --no-header file1.txt file2.txt
  cat file.txt | ./head_tail.py -n 3
  seq 20 | ./head_tail.py
  seq 4 | ./head_tail.py
"""

import argparse
import sys
from typing import List


def print_lines(
    filename: str,
    lines: List[str],
    linecount: int,
    print_header: bool,
    print_separator: bool,
) -> None:
    if print_header:
        print(f"==> {filename} <==")

    end_line = max(0, len(lines) - linecount)
    for i, line in enumerate(lines):
        if i < linecount or i >= end_line:
            print(line, end="")
        elif i == linecount and print_separator:
            print("...")

    if not lines[-1].endswith("\n"):
        print()


def process_input(args) -> None:
    if not args.files:
        args.files = ["-"]

    multiple_files = len(args.files) > 1
    for filename in args.files:
        if filename == "-":
            file = sys.stdin
            filename = "stdin"
            if len(args.files) == 1:
                args.no_header = True
        else:
            file = open(filename, "r")

        lines = file.readlines()
        print_lines(
            filename,
            lines,
            args.linecount,
            not args.no_header and multiple_files,
            args.separator,
        )

        if filename != "stdin":
            file.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Print the first and last N lines of a file or stdin."
    )
    parser.add_argument(
        "-n",
        "--linecount",
        type=int,
        default=5,
        help="Number of lines to print at the beginning and end of each file.",
    )
    parser.add_argument(
        "-H",
        "--no-header",
        action="store_true",
        help="Suppress printing the header between files.",
    )
    parser.add_argument(
        "-s",
        "--separator",
        action="store_true",
        help='Print a separator ("...") between the head and tail of each file.',
    )
    parser.add_argument(
        "files", nargs="*", help="Files to process. If none provided, read from stdin."
    )
    args = parser.parse_args()

    process_input(args)


if __name__ == "__main__":
    main()

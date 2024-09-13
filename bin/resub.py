#!/usr/bin/env python3
"""
resub.py - Bulk replace using regular expressions

PURPOSE:
    This script performs regular expression substitutions on multiple files. You can provide files or directories,
    and substitutions will be performed as specified by the user.

USAGE:
    resub.py [OPTIONS] <PATTERN> <REPLACEMENT> [file|directory] ...

OPTIONS:
    --confirm, -c
        Confirm every replacement. The script will prompt you before applying each substitution.

    --debug, -d
        Increase verbosity of debugging messages. This option can be repeated to increase verbosity.

    --dry-run, -n
        Dry run. The script will not modify files, but will simulate the replacement process and show what changes would be made.

    --from-file, -f
        Read the list of files to process from a file. Use "-" to read from STDIN.

    --match, -m <pattern>
        Only perform the substitution if lines also match the specified pattern.

    --nomatch, -V <pattern>
        Only perform the substitution if the line does NOT match the specified pattern.

    --help, -h
        Prints the help message and exits.

    --ignore-errors, -e
        Ignore errors when opening or closing files.

    --ignore-case, -i
        Make the pattern match case-insensitive.

    --recursive, -r
        Process directories recursively. The default behavior is to process all files in the specified directory
        without recursing into subdirectories.

    --verbose, -v
        Increase verbosity of output. Will print modified lines to stdout.

DESCRIPTION:

    resub.py performs regular expression substitution on multiple files. You can
    pass files or directories to the script, and it will search for and replace
    patterns in those files. The actual substitution takes place in a temporary
    file, which is then copied back over the original file if substitutions were
    made and no errors occurred. This preserves symlinks and file metadata such
    as permissions.

    The script also supports filtering lines based on additional match or
    nomatch patterns, as well as performing replacements recursively in
    directories.

    Note that this is a python port of the original resub perl tool I wrote back
    in 2006. However, that had a number of dependencies that were cumbersome to
    install.

EXAMPLES:

    # Replace "foo" with "bar" in multiple files
    $ resub.py foo bar file1 file2 file3

    # Replace files, confirming each substitution
    $ resub.py -c foo bar file1 file2

    # Replace all files in the top level of a directory
    $ resub.py foo bar my_documents

    # Replace files in directories, recursively
    $ resub.py -r foo bar my_documents your_documents

    # Case-insensitive matching
    $ resub.py -i foo bar file1

    # Replace using additional match pattern for lines.
    # Only replaces on lines that match '^tags: '
    $ resub.py -m '^tags: ' '\[|\]' "" *.md

    # read input files from stdin
    fd '\.md$' resub.py -f - foo bar


LICENSE:
    Copyright 2024 by [Jud Dagnall], all rights reserved.
    This program is free software; you can redistribute it and/or modify it under the terms of the Python Software Foundation License.

AUTHOR:
    Jud Dagnall <github@dagnall.net>
"""

import re
import os
import sys
import argparse
import logging
import tempfile
from pathlib import Path


LOG_FORMAT='%(asctime)s %(levelname)s - %(message)s'

def parse_args(args=None):
    if args is None:
        args = sys.argv[1:]  # Default to command-line arguments if not provided
    parser = argparse.ArgumentParser(description="Bulk replace using regular expressions")
    parser.add_argument("pattern", help="Regex pattern to search for")
    parser.add_argument("replacement", help="Replacement string")
    parser.add_argument("files", nargs='*', default=['.'], help="Files or directories to process")
    parser.add_argument("-c", "--confirm", action="store_true", help="Confirm every replacement")
    parser.add_argument("-d", "--debug", action="count", default=0, help="Increase verbosity of debugging messages")
    parser.add_argument("-n", "--dry-run", action="store_true", help="Dry run. Don't actually modify files.")
    parser.add_argument("-f", "--from-file", help="Read list of files to process from a file or stdin")
    parser.add_argument("-i", "--ignore-case", action="store_true", help="Ignore case in pattern matching")
    parser.add_argument("-e", "--ignore-errors", action="store_true", help="Ignore errors when opening files")
    parser.add_argument("-r", "--recursive", action="store_true", help="Process directories recursively")
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase verbosity of output")
    parser.add_argument("-m", "--match", help="Only perform substitution if lines also match this pattern")
    parser.add_argument("-V", "--nomatch", help="Only perform substitution if lines do not match this pattern")
    args = parser.parse_args(args)

    return args


def replace(file, pattern, replacement, opts):
    logging.debug(f"Processing file: {file}")

    if opts.ignore_case:
        search_pattern = re.compile(pattern, re.IGNORECASE)
    else:
        search_pattern = re.compile(pattern)


    try:
        with open(file, 'r') as infile, tempfile.NamedTemporaryFile('w', delete=False) as outfile:
            logging.debug('checking file: %s', file)

            modified = False
            for line in infile:
                original_line = line

                # Skip lines that don't match the pattern
                if not search_pattern.search(line):
                    logging.debug("No match found")
                    outfile.write(line)
                    continue

                # Skip lines that match the nomatch pattern
                if opts.nomatch and re.search(opts.nomatch, line):
                    logging.debug("Nomatch condition met, skipping")
                    outfile.write(line)
                    continue

                # Skip lines that don't match the match pattern
                if opts.match and not re.search(opts.match, line):
                    logging.debug("Match condition not met, skipping")
                    outfile.write(line)
                    continue

                # Confirmation prompt if enabled
                if opts.confirm:
                    print(f"Replace in line: {line.strip()}? (y/n/all) ", end="")
                    response = input().lower()
                    if response == 'n':
                        outfile.write(line)
                        continue
                    elif response == 'all':
                        opts.confirm = False

                # Perform the substitution
                modified = True
                line = search_pattern.sub(replacement, line)
                if opts.verbose:
                    print(f"Modified: {original_line.strip()} -> {line.strip()}")

                outfile.write(line)

            if not modified:
                logging.debug("No modifications made to file.")
                os.remove(outfile.name)
                return False

            if opts.dry_run:
                logging.info(f"Dry run: would replace content in {file}")
                os.remove(outfile.name)
                return True

        # Overwrite the original file with the modified content
        with open(file, 'w') as original_file:
            with open(outfile.name, 'r') as temp_file:
                original_file.write(temp_file.read())

        os.remove(outfile.name)
        logging.info(f"Replaced content in {file}")
        return True

    except Exception as e:
        if opts.ignore_errors:
            logging.error(f"Error processing {file}: {e}")
        else:
            logging.critical(f"Error processing {file}: {e}")
            sys.exit(1)
    return False


def process_files(files, opts, pattern, replacement):
    file_list = []

    if opts.from_file:
        if opts.from_file == '-':
            file_list = [line.strip() for line in sys.stdin]
        else:
            with open(opts.from_file) as f:
                file_list = [line.strip() for line in f.readlines()]

    if not file_list:
        for file in files:
            if os.path.isdir(file):
                if opts.recursive:
                    for root, _, filenames in os.walk(file):
                        for name in filenames:
                            file_list.append(os.path.join(root, name))
                else:
                    file_list.extend([os.path.join(file, f) for f in os.listdir(file) if os.path.isfile(os.path.join(file, f))])
            else:
                file_list.append(file)

    for file in file_list:
        if re.search(r'\.(swo|swp)$', file):
            logging.debug(f"Skipping swap file: {file}")
            continue
        replace(file, pattern, replacement, opts)

def main():
    logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT)
    opts = parse_args()

    if opts.debug == 1:
        logging.getLogger().setLevel(logging.INFO)
    elif opts.debug >= 2:
        logging.getLogger().setLevel(logging.DEBUG)

    logging.debug(f"Pattern: {opts.pattern}")
    logging.debug(f"Replacement: {opts.replacement}")
    logging.debug(f"Files: {opts.files}")

    if opts.dry_run:
        logging.warning("Dry run mode - no changes will be made.")

    process_files(opts.files, opts, opts.pattern, opts.replacement)

if __name__ == "__main__":
    main()

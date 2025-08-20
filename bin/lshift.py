#!/usr/bin/env python3
"""
Remove common leading whitespace from text based on first non-blank line.

Determines indentation level from the first non-blank line and removes
that amount of leading whitespace from all subsequent lines (only if
those leading characters are whitespace).

Example usage:
    $ echo "    def foo():
          print('hello')
          return True" | ./lshift.py

    Output:
    def foo():
        print('hello')
        return True

    $ ./lshift.py file1.txt file2.txt
    $ ./lshift.py < indented_file.txt
"""

import fileinput
import sys

lines = list(fileinput.input())
if not lines:
    sys.exit()

# Find first non-blank line
for first in lines:
    if first.strip():
        break
else:
    sys.exit()

# Get leading whitespace count
indent = len(first) - len(first.lstrip())

# Output with indent removed
for line in lines:
    # Only remove if the leading characters are whitespace
    if line[:indent].strip() == "" and len(line) > indent:
        print(line[indent:], end="")
    else:
        print(line, end="")

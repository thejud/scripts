#!/usr/bin/env python3
"""
Parse key=value pairs from stdin with support for double-quoted values.

This script reads lines from stdin and splits them into key=value pairs,
handling double-quoted values that may contain escaped quotes or commas.
The first item on each line is treated as a timestamp (not a k=v pair).

Usage:
    echo "timestamp,key1=\"value1\",key2=\"value with \\\"quotes\\\"\"" | python kvsplit.py

Output:
    Each item is printed on a separate line with comma formatting preserved.
"""
import sys


def parse_kv_line(line):
    """Parse a line containing comma-separated key=value pairs.

    Handles double-quoted values with escaped quotes.
    First item may be a timestamp (not a k=v pair).
    """
    line = line.strip()
    if not line:
        return []

    items = []
    current_item = ""
    in_quotes = False
    i = 0

    while i < len(line):
        char = line[i]

        if char == '"' and (i == 0 or line[i - 1] != "\\"):
            # Toggle quote state (only if not escaped)
            in_quotes = not in_quotes
            current_item += char
        elif char == "," and not in_quotes:
            # Split on comma only when not in quotes
            if current_item.strip():
                items.append(current_item.strip())
            current_item = ""
        else:
            current_item += char

        i += 1

    # Add the last item
    if current_item.strip():
        items.append(current_item.strip())

    return items


def main():
    """Read from stdin and parse k=v pairs, outputting each on a new line."""
    for line in sys.stdin:
        items = parse_kv_line(line)

        for i, item in enumerate(items):
            if i == 0:
                # First item might be timestamp, print as-is
                print(f"{item},")
            else:
                # Subsequent items are k=v pairs
                print(f",{item}")


if __name__ == "__main__":
    main()

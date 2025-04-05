#!/usr/bin/env python3

import sys
import argparse
import logging
import fileinput
from tdigest import TDigest

# Set up logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def read_numbers(sources):
    for line in sources:
        line = line.strip()
        if not line:
            continue
        try:
            yield float(line)
        except ValueError:
            logging.warning(f"Skipping non-numeric input: {line}")

def main():
    parser = argparse.ArgumentParser(description="Build a t-digest from a sequence of numbers.")
    parser.add_argument("files", nargs="*", help="Input file(s). If none are provided, reads from stdin.")
    args = parser.parse_args()

    digest = TDigest()

    try:
        for number in read_numbers(fileinput.input(files=args.files)):
            digest.update(number)
    except FileNotFoundError as e:
        logging.error(str(e))
        sys.exit(1)

    # Output digest summary
    print("T-Digest Summary:")
    print(f"- Count: {digest.n}")
    print(f"- Min: {digest.percentile(0):.5f}")
    print(f"- Median (50th percentile): {digest.percentile(50):.5f}")
    print(f"- 90th percentile: {digest.percentile(90):.5f}")
    print(f"- 99th percentile: {digest.percentile(99):.5f}")
    print(f"- Max: {digest.percentile(100):.5f}")

if __name__ == "__main__":
    main()

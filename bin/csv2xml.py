#!/usr/bin/env python3
import argparse
import logging
import csv
import sys
import xml.etree.ElementTree as ET
from io import StringIO

def main():
    parser = argparse.ArgumentParser(description='Convert CSV to XML.')
    parser.add_argument('input', nargs='?', help='Input CSV file. If not provided, read from stdin.')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info(f'Processing input from {args.input if args.input else "stdin"}')

    if args.input:
        with open(args.input, 'r') as f:
            csv_data = f.read()
    else:
        csv_data = sys.stdin.read()

    csv_file = StringIO(csv_data)
    csv_reader = csv.DictReader(csv_file)

    root = ET.Element('data')
    for row in csv_reader:
        record = ET.Element('record')
        for key, value in row.items():
            field = ET.SubElement(record, key)
            field.text = value.strip() if value else ''
        root.append(record)

    tree = ET.ElementTree(root)
    tree.write(sys.stdout, encoding='utf-8', xml_declaration=True)

if __name__ == '__main__':
    main()
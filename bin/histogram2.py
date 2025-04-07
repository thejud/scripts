#!/usr/bin/env python

import matplotlib.pyplot as plt
import argparse
import sys
import fileinput

def plot_histogram(data, bins, size):
    plt.figure(figsize=size)
    plt.hist(data, bins=bins, orientation='vertical')
    plt.xlabel('Frequency')
    plt.ylabel('Value')
    plt.title('Horizontal Histogram')
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot a horizontal histogram.')
    parser.add_argument('input', type=argparse.FileType('r'), 
                        help='Input file containing a series of integers, ' +
                        'one per line. "-" for STDIN', default=sys.stdin)
    parser.add_argument('-x', default=10, type=int,
        help="x size. default=%(default)s")
    parser.add_argument('-y', default=6, type=int,
        help="y size. default=%(default)s")
    parser.add_argument('--bins', type=int, default=10, help='Number of bins for the histogram.')

    args = parser.parse_args()

    data = [int(line.strip()) for line in args.input]
    plot_histogram(data, args.bins, (args.x, args.y))

#!/usr/bin/env python3

description = """brent-data.py -- Reads in Sharon Goldwater's verion of Brent data file.

  (c) Mark Johnson, 1st September 2014

"""

import argparse, re, sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin)
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'),
                        default=sys.stdout)
    args = parser.parse_args()

    for line in args.infile:
        args.outfile.write(' '.join('.'.join(word)
                                    for word in line.split()))
        args.outfile.write('\n')

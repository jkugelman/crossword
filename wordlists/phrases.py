#!/usr/bin/env python3

from argparse import ArgumentParser
import re
import sys

from lib import *

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-m', '--min_score', type=int, default=2)
    args = parser.parse_args()

    words = load_words(min_score=args.min_score)

    for line in sys.stdin:
        entry = re.sub(';.*', '', line.strip())
        for phrase in phrases(entry, words):
            print(" ".join(phrase), flush=True)

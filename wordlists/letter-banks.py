#!/usr/bin/env python3

# Finds words that use the same set of letters.

from argparse import ArgumentParser
import csv
from lib import load_words
import sys

def main():
    parser = ArgumentParser()
    parser.add_argument("--letters", type=int, required=True, help="Letter count")
    parser.add_argument("--min_count", type=int, default=2, help="Minimum number of words")
    parser.add_argument("--min_score", type=int, default=30, help="Minimum score")
    args = parser.parse_args()

    words = load_words(min_score=args.min_score)
    words_by_letters = dict()

    for word in words:
        letters = ''.join(sorted(set(word)))
        if len(letters) != args.letters:
            continue
        words_by_letters.setdefault(letters, set()).add(word)

    csv_writer = csv.writer(sys.stdout)
    for letters, words in sorted(words_by_letters.items(), key=lambda p: len(p[1]), reverse=True):
        if len(words) < args.min_count:
            continue
        csv_writer.writerow([letters, ', '.join(sorted(words))])

if __name__ == '__main__':
    main()

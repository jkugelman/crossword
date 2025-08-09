#!/usr/bin/env python3

# Carin Ash's idea

import csv
from sys import stdout

from lib import load_words

def main():
    words = load_words()
    csv_writer = csv.writer(stdout)

    for word in words:
        if 'sun' not in word:
            continue
        left, right = word.split("sun", 1)
        if 1 <= len(left) <= 2 or 1 <= len(right) <= 2:
            continue
        csv_writer.writerow([
            word, words[word],
            left, words.get(left, 0),
            right, words.get(right, 0),
        ])

if __name__ == '__main__':
    main()

#!/usr/bin/env python3

# Swap inner substrings, or swap a pair of inner letters.

from argparse import ArgumentParser
import csv
from itertools import combinations
from lib import load_words
from sys import stdout

def main():
    parser = ArgumentParser()
    parser.add_argument('-m', '--min_score', type=int, default=2)
    args = parser.parse_args()

    words = load_words(args.min_score)
    out = csv.writer(stdout)

    out.writerow([
        'word', 'score',
        'swapped', 'score',
        'i', 'j',
    ])

    for word, swapped, i, j in trade_letters(words):
        out.writerow([
            word, words[word],
            swapped, words[swapped],
            i, j
        ])

def flip_substrings(words):
    for word in sorted(words):
        for i in range(len(word) - 1):
            for length in range(2, len(word) - i):
                inner = word[i:i+length]
                renni = inner[::-1]
                if inner == renni:
                    continue

                swapped = word[:i] + renni + word[i + length:]
                if swapped not in words:
                    continue

                yield (word, swapped, inner, renni, i, length)

def trade_letters(words):
    for word in sorted(words):
        for i, j in combinations(range(len(word)), 2):
            if word[i] == word[j]:
                continue

            swapped = word[:i] + word[j] + word[i+1:j] + word[i] + word[j+1:]
            if swapped not in words:
                continue
            if word > swapped:
                continue

            yield (word, swapped, i, j)


if __name__ == '__main__':
    main()

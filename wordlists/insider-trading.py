#!/usr/bin/env python3

from argparse import ArgumentParser
import csv
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
        'inner', 'score',
        'renni', 'score',
        'i', 'length',
    ])

    for word in sorted(words):
        for i in range(1, len(word) - 1):
            for length in range(2, len(word) - i):
                inner = word[i:i+length]
                renni = inner[::-1]
                if inner == renni:
                    continue

                swapped = word[:i] + renni + word[i + length:]
                if swapped not in words:
                    continue

                scores = (words[word], words[swapped])
                min_score = min(scores)
                max_score = max(scores)
                inner_score = words.get(inner, 0)
                renni_score = words.get(inner[::-1], 0)
                out.writerow([
                    word, words[word],
                    swapped, words[swapped],
                    inner, inner_score,
                    renni, renni_score,
                    i, length,
                ])

if __name__ == '__main__':
    main()

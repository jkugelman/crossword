#!/usr/bin/env python3
#
# Detects potential duplicates in the input with n-letter overlap.
#
# Usage: `./duplicates.py 2 < entries.txt`

from itertools import groupby
import sys

def ngrams(word, n):
    return (word[i:i+n] for i in range(len(word) - (n-1)))

def main():
    n = int(sys.argv[1])

    words = [line.strip() for line in sys.stdin]
    ngram_words = sorted({(ngram, word) for word in words for ngram in ngrams(word, n)})
    ngram_words = [(k, [word for ngram, word in g]) for k, g in groupby(ngram_words, key=lambda bw: bw[0])]
    for ngram, words in ngram_words:
        if len(words) > 1:
            print(f"{ngram}: {words}")

if __name__ == '__main__':
    main()

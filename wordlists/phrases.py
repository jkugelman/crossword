#!/usr/bin/env python3

import fileinput

from merge import *

def phrases(entry, words):
    for i in range(1, len(entry)):
        prefix, suffix = entry[:i], entry[i:]
        if prefix in words:
            for phrase in phrases(suffix, words):
                yield [prefix] + phrase
    if entry in words:
        yield [entry]

if __name__ == '__main__':
    word_list = load_word_list(min_score=2)

    for line in fileinput.input():
        entry = line.rstrip()
        for phrase in phrases(entry, word_list.words):
            print(" ".join(phrase))

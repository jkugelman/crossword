#!/usr/bin/env python3

from argparse import ArgumentParser
import re
import sys

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
    word_list = {line.strip(): 50 for line in open('animal-groups.txt')}

    for line in sys.stdin:
        entry = re.sub(';.*', '', line.strip())
        for phrase in phrases(entry, word_list):
            print(" ".join(phrase))

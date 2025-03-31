#!/usr/bin/env python3

# Finds pairs of things from the same set that overlap by a letter,
# such as LIBRA + ARIES = LIBRARIES.
#
# Data sources:
# 1. https://docs.google.com/spreadsheets/d/1nq0OI8ycnkFP4Xe9QOGChpOGM8nmetBPwBX3jwhQ4OI/edit?gid=0#gid=0
# 2. Roget's Thesaurus

import csv
from itertools import permutations
from pprint import pprint
import re

from lib import *
import roget

def main():
    words = load_words()

    with open('sets-of-things.csv') as file:
        things = csv.reader(file)
        things = {
            row[1]: {_normalize(thing) for thing in row[2:]} - {''}
            for row in things
        }

    for category in roget.roget:
        for entries in roget.roget[category].values():
            for entry in entries:
                entry = _normalize(entry)
                if entry:
                    things.setdefault(category, set()).add(entry)

    for category, items in things.items():
        for permutation in permutations(items, 2):
            left, right = permutation
            if left[-1] != right[0]:
                continue
            if len(left) == 1 or len(right) == 1:
                continue
            combined = left[:-1] + right
            if combined in words:
                print(f"{left} + {right} = {combined} ({category})", flush=True)

def _normalize(thing):
    return re.sub('\W', '', thing).lower()

if __name__ == '__main__':
    main()

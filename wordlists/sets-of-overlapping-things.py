#!/usr/bin/env python3

# Finds pairs of things from the same set that overlap by a letter,
# such as LIBRA + ARIES = LIBRARIES.
#
# Data source: https://docs.google.com/spreadsheets/d/1nq0OI8ycnkFP4Xe9QOGChpOGM8nmetBPwBX3jwhQ4OI/edit?gid=0#gid=0

import csv
from itertools import permutations
from pprint import pprint
import re

from lib import *

def main():
    words = load_words()

    with open('sets-of-things.csv') as file:
        things = csv.reader(file)
        things = {
            row[1]: {
                re.sub('\W', '', thing).lower()
                for thing in row[2:]
            } - {''}
            for row in things
        }

    for category, items in things.items():
        for permutation in permutations(items, 2):
            left, right = permutation
            if left[-1] != right[0]:
                continue
            combined = left[:-1] + right
            if combined in words:
                print(f"{left} + {right} = {combined} ({category})", flush=True)

if __name__ == '__main__':
    main()

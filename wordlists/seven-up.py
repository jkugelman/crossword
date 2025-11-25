#!/usr/bin/env python3

# With Adam Wagner.
# Find words that have overlapping suffixes, like TENU(RETRACK)CIN.

import csv
from sys import stdout

from lib import load_words

def main():
    words = load_words(30)

    csv_writer = csv.writer(stdout)
    for left, right in sorted(turn_tail(words, 7).items()):
        csv_writer.writerow(['\n'.join(left), '\n'.join(right)])

def turn_tail(words, n):
    # Filter out words shorter than n characters
    words = [w for w in words if len(w) >= n]

    # Dictionaries for grouping by suffix (forward and reverse)
    forward_groups = {}
    reverse_groups = {}

    for w in words:
        suffix = w[-n:]              # last n characters
        rev_suffix = suffix[::-1]    # reversed suffix

        forward_groups.setdefault(suffix, []).append(w)
        reverse_groups.setdefault(rev_suffix, []).append(w)

    result = {}

    for suffix, key_words in forward_groups.items():
        if suffix not in reverse_groups:
            continue
        value_words = reverse_groups[suffix]

        # Avoid double counting.
        if suffix > suffix[::-1]:
            continue

        # Avoid trivial dupes.
        if len(key_words) == 1 and key_words == value_words:
            continue

        result[tuple(key_words)] = tuple(value_words)

    return result

if __name__ == '__main__':
    main()

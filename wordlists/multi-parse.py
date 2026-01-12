#!/usr/bin/env python3

# Finds phrases that can be parsed in multiple distinct ways,
# like `mount st helens` and `mounts the lens`.

from argparse import ArgumentParser
from lib import load_words, phrases

def main():
    parser = ArgumentParser()
    parser.add_argument("--min_length", type=int, default=2, help="Minimum length")
    parser.add_argument("--min_score", type=int, default=10, help="Minimum score")
    args = parser.parse_args()

    words = load_words(min_score=args.min_score)

    for word in words:
        multi = multi_parse(word, words, args.min_length)
        if multi:
            print(f"{''.join(multi[0])}: {multi}")

def multi_parse(entry, words, min_length, ignore_short=True):
    """
    Return a list of >= 2 parsings of `entry` such that no two returned parsings
    share any split points (character indices where the parsing splits `entry`).
    """
    parses = []  # list of (parsing, split_point_set)

    # Collect all valid parsings
    for parsing in phrases(entry, words, ignore_short):
        if len(parsing) < min_length:
            continue

        split_points = set()
        pos = 0
        for w in parsing[:-1]:
            pos += len(w)
            split_points.add(pos)

        parses.append((parsing, split_points))

    # Try to build a mutually disjoint set
    result = []
    used_splits = set()

    for parsing, splits in parses:
        if splits.isdisjoint(used_splits):
            result.append(parsing)
            used_splits |= splits

    return result if len(result) >= 2 else []

if __name__ == '__main__':
    main()

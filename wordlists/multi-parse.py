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

    If a candidate parsing conflicts with already-chosen ones (overlapping split
    points), we keep the shorter parsing (fewer words / fewer split points).
    """
    parses = []  # list of (parsing, split_point_set)

    for parsing in phrases(entry, words, ignore_short):
        if len(parsing) < min_length:
            continue

        split_points = set()
        pos = 0
        for w in parsing[:-1]:
            pos += len(w)
            split_points.add(pos)

        parses.append((parsing, split_points))

    # Prefer shorter parsings when conflicts occur.
    # Tie-breakers are just to make behavior deterministic.
    parses.sort(key=lambda ps: (len(ps[0]), len(ps[1]), ps[0]))

    chosen = []  # list of (parsing, split_point_set)

    for parsing, splits in parses:
        # Find which chosen parses this one conflicts with
        conflicting_idxs = [
            i for i, (_, csplits) in enumerate(chosen)
            if not splits.isdisjoint(csplits)
        ]

        if not conflicting_idxs:
            chosen.append((parsing, splits))
            continue

        # Keep the shorter one: replace *all* conflicts only if this parsing
        # is strictly shorter than each conflicting chosen parsing.
        if all(len(parsing) < len(chosen[i][0]) for i in conflicting_idxs):
            # Remove conflicts (delete from end to start so indices stay valid)
            for i in sorted(conflicting_idxs, reverse=True):
                del chosen[i]
            chosen.append((parsing, splits))
        # else: skip this parsing

    result = [p for p, _ in chosen]
    return result if len(result) >= 2 else []

if __name__ == '__main__':
    main()

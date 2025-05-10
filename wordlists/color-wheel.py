#!/usr/bin/env python3

# Generates color wheels for Jacob Reed's puzzle.

from argparse import ArgumentParser
from collections import defaultdict

from lib import load_words

def main():
    parser = ArgumentParser()
    parser.add_argument("--min_score", type=int, default=30, help="Minimum score")
    parser.add_argument("--min_length", type=int, default=3, help="Minimum length")
    parser.add_argument("--max_length", type=int, default=6, help="Maximum length")
    args = parser.parse_args()

    words = load_words(min_score=args.min_score)

    colors = {line.strip() for line in open('colors.txt')}
    colors = {
        color for color in colors
        if color in words
            and args.min_length <= len(color) <= args.max_length
    }

    for wheel in color_wheels(colors, words):
        print(f"{', '.join(wheel)} -> {', '.join(rotated(wheel))}", flush=True)

def color_wheels(colors, words):
    """
    Yield all 8-tuples `wheel = (c0, c1, ..., c7)` drawn from `colors` such that:

      1. Opposite slots have the same length:
         len(wheel[0]) == len(wheel[4]),
         len(wheel[1]) == len(wheel[5]), ...
      2. If you form a rotation of first letters (slots 0–3) and last letters (4–7)
         and shift them one slot to the right, inserting each into the next word,
         all 8 resulting strings are in `words`.

    colors: list of strings
    words: collection (set/list) of valid words
    """
    words_set = set(words)
    by_len = defaultdict(list)
    for c in colors:
        by_len[len(c)].append(c)

    opposites = {0:4,1:5,2:6,3:7,4:0,5:1,6:2,7:3}
    wheel = [None]*8
    used = set()

    def backtrack(slot):
        if slot == 8:
            # final wraparound check for slot 0
            rot = wheel[7][-1]
            if rot != wheel[0][0] and (rot + wheel[0][1:]) in words_set:
                yield tuple(wheel)
            return

        opp = opposites[slot]
        # restrict to same-length if opposite already placed
        candidates = by_len[len(wheel[opp])] if opp < slot else colors

        for c in candidates:
            if c in used:
                continue
            wheel[slot] = c
            used.add(c)

            # early prune: once slot>0, we know the rotated-in letter
            # comes from (slot-1) mod 8
            if slot != 0:
                prev = (slot-1) % 8
                rot  = wheel[prev][0] if prev < 4 else wheel[prev][-1]

                # must actually change a letter
                if slot < 4:
                    if rot == c[0] or (rot + c[1:]) not in words_set:
                        used.remove(c)
                        continue
                else:
                    if rot == c[-1] or (c[:-1] + rot) not in words_set:
                        used.remove(c)
                        continue

            yield from backtrack(slot+1)
            used.remove(c)

    yield from backtrack(0)

def rotated(wheel):
    """
    Given a tuple of 8 color‐name strings `wheel`, returns a tuple of the 8 "rotated" words.
    """
    return (
        wheel[7][-1] + wheel[0][1:],
        wheel[0][0] + wheel[1][1:],
        wheel[1][0] + wheel[2][1:],
        wheel[2][0] + wheel[3][1:],
        wheel[4][:-1] + wheel[3][0],
        wheel[5][:-1] + wheel[4][-1],
        wheel[6][:-1] + wheel[5][-1],
        wheel[7][:-1] + wheel[6][-1],
    )

if __name__ == '__main__':
    main()

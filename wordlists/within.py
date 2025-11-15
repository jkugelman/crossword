#!/usr/bin/env python3

# Given a list of needles on the command line, finds words where one needle is nested within
# another. For example: `./within.py maria juan` finds all the words that contain `marijuana`.

import sys

from lib import load_words

def main():
    words = load_words()
    needles = set(sys.argv[1:])

    for word, results in within(words, needles):
        for inner, outer, viz in results:
            print(viz)

def within(words, needles):
    """
    Yield (word, matches) where matches is a list of (inner, outer, viz).

    A word matches if it contains some substring SEG and needles inner, outer
    such that:

        SEG == outer[:k] + inner + outer[k:]

    for some k in [0, len(outer)].

    `viz` is the word with SEG wrapped as outer and inner wrapped inside:

        ... ( outer[:k] ( inner ) outer[k:] ) ...
    """
    for w in words:
        results = []

        for outer in needles:
            for inner in needles:
                # Try all possible split positions in `outer`
                for k in range(1, len(outer)):
                    combined = outer[:k] + inner + outer[k:]
                    if not combined:
                        continue

                    start = 0
                    while True:
                        idx = w.find(combined, start)
                        if idx == -1:
                            break

                        outer_start = idx
                        outer_end = idx + len(combined)

                        inner_start = outer_start + len(outer[:k])
                        inner_end = inner_start + len(inner)

                        viz = _visualize_nested(
                            w,
                            (outer_start, outer_end),
                            (inner_start, inner_end),
                        )

                        triplet = (inner, outer, viz)
                        if triplet not in results:
                            results.append(triplet)

                        # allow overlapping matches
                        start = idx + 1

        if results:
            yield w, results

def _visualize_nested(word, outer_span, inner_span):
    """
    Insert parentheses to visualize containment:

        (outer_start
        (inner_start
        inner_end)
        outer_end)

    Spans are (start, end) with end exclusive.
    """
    outer_start, outer_end = outer_span
    inner_start, inner_end = inner_span

    inserts = {}
    inserts.setdefault(outer_start, []).append("(")
    inserts.setdefault(inner_start, []).append("(")
    inserts.setdefault(inner_end, []).append(")")
    inserts.setdefault(outer_end, []).append(")")

    out = []
    for pos in range(len(word) + 1):
        if pos in inserts:
            out.append("".join(inserts[pos]))
        if pos < len(word):
            out.append(word[pos])
    return "".join(out)

if __name__ == '__main__':
    main()

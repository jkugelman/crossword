#!/bin/env python3

from collections import defaultdict
import re

from merge import load_word_list

def main():
    words = load_word_list(min_score=40).words
    words = {word for word in words if len(word) >= 7 and word[1:-1] in words}
    words = {word for word in words if not re.search('[^s]s$', word)}

    for t, l, b, r in find_interlocking_words(words):
        w = len(t)
        h = len(l)
        spells = [t[0] + t[-1] + b[0] + b[-1], t[0] + t[-1] + b[-1] + b[0]]
        flag = '*' if any(s in words for s in spells) else ''
        print(f"{w}x{h} - Top: {t}, Left: {l}, Right: {r}, Bottom: {b}, Spells: {' or '.join(spells)} {flag}", flush=True)


def find_interlocking_words(words):
    results = []
    # Remove duplicates if any
    unique_words = list(set(words))

    # Group words by length
    words_by_length = defaultdict(list)
    for word in unique_words:
        words_by_length[len(word)].append(word)

    # Group words by their first letter
    words_by_first = defaultdict(list)
    for word in unique_words:
        words_by_first[word[0]].append(word)

    # Loop through potential candidates for t, b, l, and r
    for t in unique_words:
        # 'b' must have the same length as 't'
        for b in words_by_length[len(t)]:
            # 'l' must start with the same letter as 't'
            for l in words_by_first[t[0]]:
                # 'r' must start with the same letter as the last letter of 't'
                for r in words_by_first[t[-1]]:
                    # 'l' and 'r' must have the same length
                    if len(l) != len(r):
                        continue
                    # Check the other two interlocking conditions:
                    if l[-1] != b[0]:
                        continue
                    if r[-1] != b[-1]:
                        continue
                    # The words must all be different
                    if len({t, l, r, b}) != 4:
                        continue
                    # All conditions met, add the quadruple.
                    yield (t, l, r, b)

# Example usage:
if __name__ == "__main__":
    main()

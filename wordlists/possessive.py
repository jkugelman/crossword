#!/usr/bin/env python3

from merge import *
from phrases import *

if __name__ == '__main__':
    word_list = load_word_list(min_score=40)
    words = set(word_list.words)

    for word in sorted(words):
        for phrase in phrases(word, words):
            plurals = [(i, plural) for (i, plural) in enumerate(phrase) if i+1 < len(phrase) and len(plural) >= 4 and plural.endswith('s') and plural[:-1] in words]
            for (i, plural) in plurals:
                pluralized = list(phrase)
                pluralized[i] = plural[:-1] + "'s"
                print(f"{len(''.join(phrase)):2} {' '.join(pluralized).upper()}")

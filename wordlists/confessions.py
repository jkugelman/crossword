#!/usr/bin/env python3

# Move "I" to the front of entries
# e.g. TOOK PANS -> I TOOK PANS
# For @zach on Discord

from merge import *
from phrases import *

def main():
    word_list = load_word_list(min_score=30).words

    for word in word_list:
        if word.count('i') != 1:
            continue
        if word.startswith('i'):
            continue

        old = word
        new = old.replace('i', '')

        if new.replace('i', '') not in word_list:
            continue

        for phrase in phrases(new, word_list):
            print(f"{old} -> i{new} (i {' '.join(phrase)})")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3

import collections
import pronouncing
import re
import sys

def main():
    for (word, replacements) in phonetic_map(sys.argv[1], sys.argv[2]):
        print(f"{word}: {replacements}", flush=True)

def phonetic_map(in_phones, out_phones, *args, **kwargs):
    for word in pronouncing.search(in_phones):
        replacements = set()

        for phones in pronouncing.phones_for_word(word):
            pattern = re.sub(r'\b' + in_phones + r'\b', out_phones, phones, *args, **kwargs)
            if pattern == phones:
                continue
            if words := pronouncing.search(f'^{pattern}$'):
                replacements.update(words)

        if replacements:
            yield (word, replacements)

if __name__ == '__main__':
    main()

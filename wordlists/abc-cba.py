#!/usr/bin/env python3

import pronouncing
import re

def main():
    for word in pronouncing.search(''):
        for phones in pronouncing.phones_for_word(word):
            if pronouncing.syllable_count(phones) < 3:
                continue
            for mirror_phones in generate_mirrors(phones.split()):
                z, y, x = mirror_phones
                if not all(any(c.isdigit() for mp in mps for c in mp) for mps in mirror_phones):
                    continue
                if x == z:
                    continue
                mirror_words = set(pronouncing.search('^' + re.sub(r'\d', r'\\d*', ' '.join(z + y + x)) + '$'))
                mirror_words.discard(word)
                if mirror_words:
                    print(f"{word} -> {list(sorted(mirror_words))}", flush=True)

def generate_mirrors(a):
    n = len(a)

    # Iterate over all possible ways to split a into three non-empty sublists
    for i in range(1, n-1):
        for j in range(i+1, n):
            x, y, z = a[:i], a[i:j], a[j:]
            yield [z, y, x]

if __name__ == '__main__':
    main()

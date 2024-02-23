#!/usr/bin/env python3

import fileinput
from itertools import groupby

wordlist = {line.split(';')[0] for line in fileinput.input()}
wordlist = sorted(wordlist, key=lambda w: sorted(w))
anagrams = sorted(list(sorted(words)) for _, words in groupby(wordlist, key=lambda w: sorted(w)))

for anagram in anagrams:
    if len(anagram) > 1:
        print(','.join(anagram))

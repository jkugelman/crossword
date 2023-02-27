#!/usr/bin/env python3

from collections import Counter
from wordlists.merge import *

wl = load_word_list()

print(sorted(
    [
        word
        for word in wl.words
        if len(set(Counter(word).values())) == 1
            and list(Counter(word).values())[0] > 1
            and len(Counter(word).values()) > 1
            and not any(
                word == word[:len(word)//n]*n
                for n in range(2, 10)
            )
            # and all(v in word for v in 'aeiouy')
    ],
    key=len,
))

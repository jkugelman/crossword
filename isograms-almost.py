#!/usr/bin/env python3

from collections import Counter
import string
from wordlists.merge import *

wl = load_word_list()

def without(word, letter):
    return re.sub(letter, '', word, count=1)

answer = {
    leftover: sorted(
            [
                word
                for word in wl.words
                if leftover in word
                    and len(word) >= 10
                    and len(set(Counter(without(word, leftover)).values())) == 1
                    and list(Counter(without(word, leftover)).values())[0] > 1
                    and len(Counter(without(word, leftover)).values()) > 1
                    and not any(
                        without(word, leftover) == without(word, leftover)[:len(word)//n]*n
                        for n in range(2, 10)
                    )
                    # and all(v in word for v in 'aeiouy')
            ],
            key=len,
        )
    for leftover in string.ascii_lowercase
}

for letter, words in answer.items():
    print(f'{letter}: {", ".join(words)}')

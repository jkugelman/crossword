#!/usr/bin/env python3

from merge import *

def phrases(word, words):
    for i in range(1, len(word)):
        prefix, suffix = word[:i], word[i:]
        if prefix in words:
            for phrase in phrases(suffix, words):
                yield [prefix] + phrase
    if word in words:
        yield [word]

if __name__ == '__main__':
    word_list = load_word_list(min_score=2)
    words = set(word_list.words)

    for word in words:
        for phrase in phrases(word, words):
            if len(phrase) == 4 and phrase[0][0] == phrase[3][0] and phrase[1][0] == phrase[2][0]:
                print(" ".join(phrase))

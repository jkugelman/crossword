#!/usr/bin/env python3

from merge import *

word_list = load_word_list()
words = set(word_list.words)
words.update({
    'a',
    'ad',
    'am',
    'an',
    'as',
    'at',
    'ax',
    'be',
    'by',
    'do',
    'go',
    'he',
    'hi',
    'i',
    'if',
    'in',
    'is',
    'it',
    'me',
    'my',
    'no',
    'of',
    'oh',
    'on',
    'or',
    'ox',
    'so',
    'to',
    'up',
    'us',
    'we',
})
words.difference_update({
    'b',
    'c',
    'd',
    'e',
    'f',
    'g',
    'h',
    'j',
    'k',
    'l',
    'm',
    'n',
    'o',
    'p',
    'q',
    'r',
    's',
    't',
    'u',
    'v',
    'w',
    'x',
    'y',
    'z',
})

def phrases(word, words):
    for i in range(1, len(word)):
        prefix, suffix = word[:i], word[i:]
        if prefix in words:
            for phrase in phrases(suffix, words):
                yield [prefix] + phrase
    if word in words:
        yield [word]

for word in words:
    for phrase in phrases(word, words):
        if len(phrase) == 4 and phrase[0][0] == phrase[3][0] and phrase[1][0] == phrase[2][0]:
            print(" ".join(phrase))

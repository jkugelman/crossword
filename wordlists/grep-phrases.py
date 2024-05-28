#!/usr/bin/env python3

import fileinput

from merge import *

def load_word_list():
    word_list = WordList()
    word_list.load('wordlist.txt', [filter(min_score=50)])
    return word_list

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

def is_phrase(word, words):
    if word == '' or word in words:
        return True

    for i in range(1, len(word)):
        prefix, suffix = word[:i], word[i:]
        if prefix in words and is_phrase(suffix, words):
            return True

for word in fileinput.input():
    word = word.strip()
    if is_phrase(word, words):
        print(word)

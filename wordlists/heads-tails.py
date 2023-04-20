#!/usr/bin/env python3

from merge import *

def load_word_list():
    word_list = WordList()
    word_list.load('merged.txt', [filter(min_score=50, min_length=3)])
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
words.update({
    'and',
    'but',
    'for',
    'itd',
    'its',
    'itll',
    'the',
    'with',
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

def phrase_parsings(word):
    if word == '':
        return

    if word in words:
        yield [len(word)]

    for i in range(1, len(word)):
        prefix, suffix = word[:i], word[i:]
        if prefix in words:
            for parsing in phrase_parsings(suffix):
                yield [len(prefix)] + parsing

def split_up(word, parsing):
    split_word = []
    for p in parsing:
        split_word.append(word[:p])
        word = word[p:]
    return ' '.join(split_word)

for word in words:
    word = word.strip()
    count = word.count('h') + word.count('t')

    if count == 0:
        continue

    parsings = list(phrase_parsings(word))
    swapped = word.replace('h', 'H').replace('t', 'h').replace('H', 't')
    for swapped_parsing in phrase_parsings(swapped):
        if swapped_parsing in parsings:
            print(f"(swaps={count}) (len={len(word)}) {split_up(swapped, swapped_parsing)} ({split_up(word, swapped_parsing)})")

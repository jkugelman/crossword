#!/usr/bin/env python3

import re

from itertools import chain, combinations
from merge import load_word_list

def main():
    word_list = load_word_list(min_score=30)
    word_list = word_list.words.keys()

    a_word_list = {re.sub('er$', 'a', word) for word in word_list}
    a_to_er = {re.sub('er$', 'a', word): word for word in word_list if word.endswith('er')}
    del a_to_er['a']

    for entry in word_list:
        for phrase in phrases(entry, a_word_list):
            if sum(1 for word in phrase if word in a_to_er) < 2:
                continue
            er_version = [a_to_er.get(word, word) for word in phrase]
            print(f"{entry} -> {''.join(er_version)}")

def phrases(entry, word_list):
    for i in range(1, len(entry)):
        prefix, suffix = entry[:i], entry[i:]
        if prefix in word_list:
            for phrase in phrases(suffix, word_list):
                yield [prefix] + phrase
    if entry in word_list:
        yield [entry]

if __name__ == '__main__':
    main()

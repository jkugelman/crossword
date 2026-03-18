#!/usr/bin/env python3

import os
import re

from lib import load_words, save_words

def main():
    words = load_words(bonuses=True)

    save_words(words, 'wordlist.txt', scores=True)
    save_words(words, 'unscored.txt', scores=False, min_score=20)
    save_words(words, 'orca-wordlist.txt', scores=True, map_filter=orca)

def orca(word, score):
    if len(word) <= 3 and score < 40:
        return None
    elif len(word) >= 8 and score < 50:
        return None
    elif score < 40:
        return None
    return word.upper(), score

if __name__ == '__main__':
    main()

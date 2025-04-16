#!/usr/bin/env python3

import os
import re

from lib import load_words, save_words

if __name__ == '__main__':
    words = load_words(bonuses=True)
    save_words(words, 'wordlist.txt', scores=True)
    save_words(words, 'unscored.txt', scores=False, min_score=20)

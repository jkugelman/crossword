#!/usr/bin/env python3

from argparse import ArgumentParser

from merge import *
from phrases import phrases

def main():
    parser = ArgumentParser()
    parser.add_argument('-m', '--min', type=int, default=2)
    args = parser.parse_args()

    word_list = load_word_list(min_score=args.min)
    word_list = word_list.words

    for entry in word_list:
        for phrase in phrases(entry, word_list):
            phrase = list(phrase)
            if len(phrase) >= 2 and all(word+'y' in word_list for word in phrase):
                print(' '.join(word+'y' for word in phrase))

if __name__ == '__main__':
    main()

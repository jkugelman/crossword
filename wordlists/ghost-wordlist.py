#!/usr/bin/env python3

# Builds a wordlist of "ghost" words that are valid words when letters are removed.
# The ghost letters are replaced by Circled Letters: ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ.
# Regex: `[Ⓐ-Ⓩ]`

from argparse import ArgumentParser
import sys

from lib import *

def main():
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-l', '--letters', action='store_true')
    group.add_argument('-s', '--substrings', action='store_true')
    args = parser.parse_args()

    if args.letters:
        ghost_generator = ghost_letters
    elif args.substrings:
        ghost_generator = ghost_substrings
    else:
        parser.print_usage(sys.stderr)
        sys.exit(1)

    words = load_words()

    for ghost, score in ghost_generator(words):
        print(f"{ghost};{score}")

def ghost_letters(words):
    for longer in words:
        for i in range(len(longer)):
            shorter = longer[:i] + longer[i+1:]
            ghost = longer[:i] + ghostify(longer[i], 'Ⓐ') + longer[i+1:]

            if shorter in words:
                score = min(words[longer], words[shorter])
                yield ghost, score

def ghost_substrings(words):
    for longer in words:
        for i in range(len(longer)):
            for j in range(i + 1, len(longer)):
                shorter = longer[:i] + longer[j:]
                ghost = longer[:i] + ghostify(longer[i:j], 'Ⓐ') + longer[j:]

                if shorter in words:
                    score = min(words[longer], words[shorter])
                    yield ghost, score

def ghostify(s, a):
    return ''.join(chr(ord(a) + (ord(c) - ord('a'))) for c in s)

if __name__ == '__main__':
    main()

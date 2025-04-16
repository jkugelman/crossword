#!/usr/bin/env python3

# Builds a wordlist of "ghost" words that are valid words when letters are removed.
#
# * With `--letters <N>`, 1-N ghost letters are replaced by ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ (`[Ⓐ-Ⓩ]`).
# * With `--substrings`, ghost substrings are replaced.
# * With `--spaces`, ghost spaces ◯ are added between letters.
#
# ```
# $ ./ghost-wordlist.py --letters 1 > ghost-letters-1.txt
# $ ./ghost-wordlist.py --letters 2 > ghost-letters-2.txt
# $ ./ghost-wordlist.py --letters 3 > ghost-letters-3.txt
# $ ./ghost-wordlist.py --spaces > ghost-spaces.txt
# ```

from argparse import ArgumentParser
from itertools import combinations
import sys

from lib import load_words

def main():
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--letters', type=int)
    group.add_argument('--substrings', action='store_true')
    group.add_argument('--spaces', action='store_true')
    args = parser.parse_args()

    if args.letters:
        ghost_generator = lambda words: ghost_letters(args.letters, words)
    elif args.substrings:
        ghost_generator = ghost_substrings
    elif args.spaces:
        ghost_generator = ghost_spaces
    else:
        parser.print_usage(sys.stderr)
        sys.exit(1)

    words = load_words()

    for ghost, score in ghost_generator(words):
        print(f"{ghost};{score}")

def ghost_letters(n, words):
    for longer in words:
        for n in range(1, n + 1):
            for indices in combinations(range(len(longer)), n):
                shorter = remaining = ''.join(c for i, c in enumerate(longer) if i not in indices)
                if shorter in words:
                    ghost = remaining = ''.join((ghostify(c, 'Ⓐ') if i in indices else c) for i, c in enumerate(longer))
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

def ghost_spaces(words):
    for word, score in words.items():
        for i in range(len(word) + 1):
            ghost = word[:i] + '◯' + word[i:]
            yield ghost, score

def ghostify(s, a):
    return ''.join(chr(ord(a) + (ord(c) - ord('a'))) for c in s)

if __name__ == '__main__':
    main()

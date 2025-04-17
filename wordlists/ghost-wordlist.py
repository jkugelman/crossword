#!/usr/bin/env python3

# Builds a wordlist of "ghost" words that are valid words when letters are removed.
#
# * With `--letters`, single ghost letters are replaced by `[Ⓐ-Ⓩ]`, doubles by `[⒜-⒵]`.
#   ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ
#   ⒜⒝⒞⒟⒠⒡⒢⒣⒤⒥⒦⒧⒨⒩⒪⒫⒬⒭⒮⒯⒰⒱⒲⒳⒴⒵
# * With `--substrings`, ghost substrings are replaced.
# * With `--spaces`, ghost spaces ◯ are added between letters.
#
# Run `./ghosts-make` to remake all of the ghost wordlists.

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
    if n == 1:
        yield from ghost_letters_impl(1, 'Ⓐ', words)
    elif n == 2:
        yield from ghost_letters_impl(2, '⒜', words)
    else:
        print(f"n>2 not supported", file=sys.stderr)
        sys.exit(1)

def ghost_letters_impl(n, a, words):
    for longer in words:
        if len(longer) - n < 3:
            continue
        for indices in combinations(range(len(longer)), n):
            shorter = remaining = ''.join(c for i, c in enumerate(longer) if i not in indices)
            if shorter in words:
                ghost = remaining = ''.join((ghostify(c, a) if i in indices else c) for i, c in enumerate(longer))
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

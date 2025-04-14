#!/usr/bin/env python3

# Converts a string into circled "ghost" letters.
# See `ghost-wordlist.py` for context.

import fileinput
from string import ascii_lowercase

def main():
    for line in fileinput.input():
        print(''.join((chr(ord(c) - ord('a') + ord('Ⓐ')) if c in ascii_lowercase else c) for c in line.rstrip()))

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
#
# Prints the cryptogram-style letter pattern for each input line.
# Could be used to finding words that could sub for each other.

import fileinput
import string

def letter_pattern(text):
    mapping = dict()
    count = 0
    pattern = ''

    for letter in text.upper():
        # Space or other non-letter.
        if not letter.isupper():
            pattern += letter
            continue
        # First time we're seeing this letter? Assign it the next available mapping.
        if letter not in mapping:
            mapping[letter] = string.ascii_uppercase[count]
            count += 1
        # Add the mapped letter to the output.
        pattern += mapping[letter]

    return pattern

if __name__ == '__main__':
    for line in fileinput.input():
        text = line.rstrip()
        print(f"{text}\t{letter_pattern(text)}")

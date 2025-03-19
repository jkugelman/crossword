#!/usr/bin/env python3

# Finds words containing states, but one letter off.
# Collaboration with @zach on Discord.

from collections import defaultdict
from pprint import pprint
import re
import string
import sys

from merge import load_word_list

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <min_length> <max_length>", file=sys.stderr)
        sys.exit(1)

    min_length = int(sys.argv[1])
    max_length = int(sys.argv[2])

    words = load_word_list(min_score=40).words

    states = [
        "alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana", "maine", "maryland", "massachusetts", "michigan", "minnesota", "mississippi", "missouri", "montana", "nebraska", "nevada", "newhampshire", "newjersey", "newmexico", "newyork", "northcarolina", "northdakota", "ohio", "oklahoma", "oregon", "pennsylvania", "rhodeisland", "southcarolina", "southdakota", "tennessee", "texas", "utah", "vermont", "virginia", "washington", "westvirginia", "wisconsin", "wyoming",
    ]

    # Words by length.
    words_by_length = {length: set() for length in range(min_length, max_length + 1)}
    for word in words:
        if min_length <= len(word) <= max_length:
            words_by_length[len(word)].add(word)

    # Regexes by letter then state.
    regexes = {}
    for letter in string.ascii_lowercase:
        regexes[letter] = {}
        for state in states:
            regexes[letter][state] = re.compile('|'.join(
                state[:i] + letter + state[i + 1:]
                for i in range(0, len(state))
                if state[i] != letter
            ))

    # Find entries.
    for letter in string.ascii_lowercase:
        for length in range(min_length, max_length + 1):
            for word in words_by_length[length]:
                for state in states:
                    if re.search(regexes[letter][state], word):
                        print(f"{letter},{len(word)},{state},{word}", flush=True)

if __name__ == '__main__':
    main()

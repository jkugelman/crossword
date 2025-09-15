#!/usr/bin/env python3

# Finds rhyming phrases.

from itertools import product
from lib import load_words, phrases
from pronouncing import phones_for_word
import re
import readline
from sys import argv, stderr

def main():
    words = load_words()

    entry_phones = list(phones_for_entries(
        words,
        words,
    ))

    while True:
        try:
            query = input('> ')
        except EOFError:
            break
        rhymes = set(rhyming_phrases(query, entry_phones, words))
        rhymes -= {query}
        rhymes = list(sorted(rhymes))
        print(rhymes)

def rhyming_phrases(query, entry_phones, words, ignore_short=True):
    for arg_phones in phones_for_entry(query, words, ignore_short):
        rhyme_pattern = re.compile(
            ''.join(r'\D*' + re.sub(r'\d', r'\\d', rhyming_part(p)) for p in arg_phones) + '$',
        )
        for phrase, phrase_phones in entry_phones:
            if rhyme_pattern.match(' '.join(phrase_phones)):
                yield phrase

def phones_for_entries(entries, words, ignore_short=True):
    for entry in entries:
        for phones in phones_for_entry(entry, words, ignore_short):
            yield entry, phones

def phones_for_entry(entry, words, ignore_short=True):
    for phrase in phrases(entry, words, ignore_short):
        phones_for_words = (phones_for_word(word) for word in phrase)
        for phones_combo in product(*phones_for_words):
            yield phones_combo

def rhyming_part(phones):
    phones_list = phones.split()
    for i in range(len(phones_list) - 1, 0, -1):
        if phones_list[i].endswith('1'):
            return ' '.join(phones_list[i:])
    return phones

if __name__ == '__main__':
    main()

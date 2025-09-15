#!/usr/bin/env python3

# Finds rhyming phrases. Standalone version for Adam Wagner.

from itertools import product
from pronouncing import phones_for_word
import re
import readline
from sys import argv, stderr

def main():
    if len(argv) <= 1:
        print(f"Usage: {argv[0]} <wordlist.txt>...", file=stderr)
        return 1

    words = load_words(argv[1:])

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

def load_words(paths):
    words = {}
    for path in paths:
        with open(path) as file:
            for line in file:
                word, score, *_ = line.strip().lower().split(';')
                if word not in words:
                    words[word] = int(score)
    return words

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

def phrases(entry, words, ignore_short=True):
    """
    Figures out if `entry` can be made from any combination of words in `words`. All valid
    splittings are yielded.

    If `ignore_short` is true (the default), 1- and 2-letter words with score < 50 are ignored.
    This way "a" and "I" and "of/we/it" can be used, but not abbreviations like "ep" and "rd".
    """
    for i in range(1, len(entry)):
        prefix, suffix = entry[:i], entry[i:]

        if prefix not in words:
            continue
        if ignore_short and len(prefix) <= 2 and words[prefix] < 50:
            continue
        for phrase in phrases(suffix, words):
            yield [prefix] + phrase

    if entry not in words:
        return
    if ignore_short and len(entry) <= 2 and words[entry] < 50:
        return
    yield [entry]

def rhyming_part(phones):
    phones_list = phones.split()
    for i in range(len(phones_list) - 1, 0, -1):
        if phones_list[i].endswith('1'):
            return ' '.join(phones_list[i:])
    return phones

if __name__ == '__main__':
    main()

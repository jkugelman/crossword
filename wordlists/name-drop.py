#!/usr/bin/env python3

# For puzzle with Kathy Simonson.
# Finds entries like POKEMON which can be extended to POKE MONTY.

import csv
from pygtrie import Trie
from sys import stdout

from lib import load_words, parts_of_speech

def main():
    words = load_words()
    names = {line.split(',')[0] for line in open('first-names.csv')}

    csv_writer = csv.writer(stdout)
    csv_writer.writerow(['Entry', 'Circled letter', 'Verb', 'Suffix', 'Names', 'Entry score', 'Verb score', 'Names score'])
    for word, verb, suffix, names in name_drops(words, names):
        word_score = words[word]
        verb_score = words.get(verb, 0)
        names_score = max(words.get(name, 0) for name in names)
        csv_writer.writerow([
            word.upper(),
            '',
            verb,
            suffix,
            ', '.join(names),
            word_score,
            verb_score,
            names_score,
        ])

def name_drops(words, names):
    names_trie = Trie()
    for name in names:
        names_trie[name] = True

    for word in sorted(words):
        for i in range(2, len(word) - 2):
            verb, suffix = word[:i], word[i:]
            if 'verb' not in parts_of_speech(verb):
                continue
            if not names_trie.has_subtrie(suffix):
                continue
            names = {''.join(name) for name in names_trie.keys(suffix)} - {suffix}
            if not names:
                continue
            yield word, verb, suffix, names

if __name__ == '__main__':
    main()

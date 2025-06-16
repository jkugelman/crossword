#!/usr/bin/env python3

# Finds S -> SH word pairings based on pronunciation, e.g. `cease -> sheesh`.

from lib import load_words
import pronouncing
import re

def main():
    words = load_words(40)
    for s_word, sh_words in s_to_sh_words(words):
        print(f"{s_word} -> {', '.join(sh_words)}")

def s_to_sh_words(words):
    s_words = pronouncing.search(r'\bS\b')
    s_words = (
        s_word
        for s_word in sorted(set(s_words))
        if s_word in words
    )
    for s_word in s_words:
        sh_words = {
            sh_word
            for s_phones in pronouncing.phones_for_word(s_word)
            for sh_word in pronouncing.search(
                '^' + re.sub(
                    r'\bER\d\b|\bUH\d R\b',
                    r'(ER\\d|UH\\d R)',
                    re.sub(r'\d', r'\\d', re.sub(r'\bS|Z\b', 'SH', s_phones))
                ) + '$',
            )
            if sh_word in words and sh_word != s_word
        }
        if sh_words:
            yield (s_word, sh_words)

if __name__ == '__main__':
    main()

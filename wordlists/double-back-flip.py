#!/usr/bin/env python3

from fnmatch import fnmatch

from merge import WordList, filter
from phrases import phrases

def load_word_list():
    word_list = WordList()
    word_list.load('wordlist.txt', [filter(min_score=30, min_length=2)])
    return word_list

def build_entries_with_words(wordlist):
    entries_with_words = dict()
    for word in wordlist:
        for i in range(len(word)):
            for j in range(i + 1, len(word) + 1):
                if word[i:j] in wordlist:
                    entries_with_words.setdefault(word[i:j], set()).add(word)
    return entries_with_words

def flipped(word):
    if len(word) <= 2 or word[-1] == word[-2]:
        return None
    return word[:-2] + word[-1] + word[-2]

def red(word):
    return f"\033[31m{word}\033[0m"

def blue(word):
    return f"\033[36m{word}\033[0m"

wordlist = set(load_word_list().words.keys())
wordlist -= {
    'aah',
    'aahs',
    'aer',
    'akc',
    'als',
    'alti',
    'ami',
    'asa',
    'atl',
    'baer',
    'baes',
    'baht',
    'bene',
    'bete',
    'boyd',
    'btu',
    'byu',
    'cani',
    'canti',
    'cma',
    'dae',
    'dei',
    'der',
    'dian',
    'eer',
    'ely',
    'eso',
    'est',
    'foer',
    'foto',
    'ger',
    'gest',
    'ing',
    'inot',
    'isr',
    'mer',
    'por',
    'pre',
    'roto',
    'rd',
    'rds',
    'rea',
    'sno',
    'ste',
    'swe',
    'tae',
    'tai',
    'tas',
    'tba',
    'wha',
    'wahs',
}
entries_with_words = build_entries_with_words(wordlist)
flippable = {word for word in wordlist if flipped(word) in wordlist}

for word1 in sorted(flippable):
    for word2 in sorted(flippable):
        if word1 == word2 or word1 == flipped(word2):
            continue
        if word1 in word2 or word2 in word1:
            continue
        for entry in entries_with_words[word1] & entries_with_words[word2]:
            if not fnmatch(entry, f"*{word1}*{word2}*"):
                continue
            parts = entry.replace(word1, "|").replace(word2, "|").split("|")
            if not all(any(True for _ in phrases(part, wordlist)) for part in parts if part):
                continue
            orig_entry = entry.replace(word1, red(word1)).replace(word2, blue(word2))
            flipped_entry = entry.replace(word1, red(flipped(word1))).replace(word2, blue(flipped(word2)))
            print(f"{orig_entry} -> {flipped_entry}")

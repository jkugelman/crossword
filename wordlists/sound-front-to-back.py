#!/usr/bin/env python3

# Finds phrase pairs where the first phoneme has been moved to the end,
# like PSYCH UP -> EYE CUPS.

from collections import defaultdict
from itertools import combinations, product
from lib import load_words, phrases
from nltk import edit_distance
from pronouncing import phones_for_word, search
from sys import stderr

def main():
    words = load_words()

    entries_and_phones = list(phones_for_entries(
        words,
        words,
    ))

    word_pairs = sound_front_to_back_pairs(entries_and_phones)
    word_pairs = sorted(word_pairs, key=lambda pair: (-edit_distance(pair[0], pair[1]), pair))

    for a, b in word_pairs:
        print(f"{a} <-> {b}")

def phones_for_entries(entries, words, ignore_short=True):
    for entry in entries:
        for phones in phones_for_entry(entry, words, ignore_short):
            yield entry, phones

def phones_for_entry(entry, words, ignore_short=True):
    for phrase in phrases(entry, words, ignore_short):
        phones_for_words = (phones_for_word(word) for word in phrase)
        for phones_combo in product(*phones_for_words):
            yield ' '.join(phones_combo)

def sound_front_to_back_pairs(phones_for_entries):
    """
    phones_for_entries: list[tuple[str, str]]
        Each tuple is (word, "space-separated phones")
    Returns a sorted list of unique word pairs (w1, w2) where one pronunciation
    is exactly the other with the first *consonant* phone moved to the end.
    """
    # Tokenize once
    tokenized = [(w, ph.split()) for (w, ph) in phones_for_entries]

    # sources: forms BEFORE the move  [x] + seq
    #   key = (tuple(seq), x)
    # dests: forms AFTER the move     seq + [x]
    #   key = (tuple(seq), x)
    sources = defaultdict(list)
    dests = defaultdict(list)

    for idx, (w, toks) in enumerate(tokenized):
        if not toks:
            continue
        # before-move signature
        x_src = toks[0]
        if not x_src[-1].isdigit():
            seq_src = tuple(toks[1:])
            sources[(seq_src, x_src)].append((w, idx, toks))

        # after-move signature
        x_dst = toks[-1]
        seq_dst = tuple(toks[:-1])
        dests[(seq_dst, x_dst)].append((w, idx, toks))

    # Pair up matching source/dest buckets
    word_pairs = set()
    for key in set(sources).intersection(dests):
        for (w1, i1, t1), (w2, i2, t2) in product(sources[key], dests[key]):
            if i1 == i2:
                continue            # same entry
            if w1 == w2:
                continue            # skip same-word pairs; remove if you want them
            if t1 == t2:
                continue            # identical pronunciation (e.g., single-phone); not a move
            word_pairs.add((w1, w2))

    return word_pairs

if __name__ == '__main__':
    main()

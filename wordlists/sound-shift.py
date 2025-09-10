#!/usr/bin/env python3

# Sound shift script inspired by Adam Wagner's FIRETRUCK / FRIAR TUCK find.
# Finds phrase pairs where one phoneme has been phonetically moved.

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

    word_pairs = sound_shift_pairs(entries_and_phones)
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

def sound_shift_pairs(phones_for_entries):
    """
    phones_for_entries: list[tuple[str, str]]
        Each tuple is (word, "space-separated phones")
    Returns a sorted list of unique word pairs (w1, w2) where the phones differ
    only by moving exactly one identical phone to a new position.
    """
    # Tokenize phones once
    tokenized = [(w, ph.split()) for (w, ph) in phones_for_entries]

    # Index by (remaining_sequence_after_removal, removed_phone)
    # Value: list of (word, entry_index, removed_pos)
    buckets = defaultdict(list)

    for entry_idx, (word, toks) in enumerate(tokenized):
        for i in range(len(toks)):
            rem = tuple(toks[:i] + toks[i+1:])
            removed_phone = toks[i]
            buckets[(rem, removed_phone)].append((word, entry_idx, i))

    # Build unique word pairs from buckets with >= 2 entries
    word_pairs = set()

    for (_, _), entries in buckets.items():
        if len(entries) < 2:
            continue
        # Any two entries in the same bucket share the same remaining sequence
        # and the same removed phone => a move (provided removed positions differ)
        for (w1, idx1, pos1), (w2, idx2, pos2) in combinations(entries, 2):
            if idx1 == idx2:
                continue  # same entry
            if pos1 == pos2:
                continue  # identical phrases; not a "move"
            if w1 == w2:
                continue  # skip same-word pairs; remove this line if you want them included
            # Add as an unordered pair so duplicates collapse
            word_pairs.add(tuple(sorted((w1, w2))))

    # Sort the results by length descending, then alphabetically ascending
    return word_pairs

if __name__ == '__main__':
    main()

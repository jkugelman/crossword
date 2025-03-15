#!/usr/bin/env python3

# Finds entries where <min_changes> letters can be incremented by <n> to become a different entry.

import argparse
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import permutations, product

from merge import *

def main():
    args = parse_arguments()

    min_word_length = args.min_word_length
    max_total_length = args.max_total_length
    min_changes_per_word = args.min_changes_per_word
    meta = args.meta

    banned = {
        'lettera', 'letterb', 'letterc', 'letterd', 'lettere', 'letterf', 'letterg', 'letterh', 'letteri', 'letterj', 'letterk', 'letterl', 'letterm', 'lettern', 'lettero', 'letterp', 'letterq', 'letterr', 'lettert', 'letteru', 'letterv', 'letterw', 'letterx', 'lettery', 'letterz',
        'capitala', 'capitalb', 'capitalc', 'capitald', 'capitale', 'capitalf', 'capitalg', 'capitalh', 'capitali', 'capitalj', 'capitalk', 'capitall', 'capitalm', 'capitaln', 'capitalo', 'capitalp', 'capitalq', 'capitalr', 'capitalt', 'capitalu', 'capitalv', 'capitalw', 'capitalx', 'capitaly', 'capitalz',
        'lowercasea', 'lowercaseb', 'lowercasec', 'lowercased', 'lowercasee', 'lowercasef', 'lowercaseg', 'lowercaseh', 'lowercasei', 'lowercasej', 'lowercasek', 'lowercasel', 'lowercasem', 'lowercasen', 'lowercaseo', 'lowercasep', 'lowercaseq', 'lowercaser', 'lowercases', 'lowercaset', 'lowercaseu', 'lowercasev', 'lowercasew', 'lowercasex', 'lowercasey', 'lowercasez',
        'silenta', 'silentb', 'silentc', 'silentd', 'silente', 'silentf', 'silentg', 'silenth', 'silenti', 'silentj', 'silentk', 'silentl', 'silentm', 'silentn', 'silento', 'silentp', 'silentq', 'silentr', 'silents', 'silentt', 'silentu', 'silentv', 'silentw', 'silentx', 'silenty', 'silentz',
        'softa', 'softb', 'softc', 'softd', 'softe', 'softf', 'softg', 'softh', 'softi', 'softj', 'softk', 'softl', 'softm', 'softn', 'softo', 'softp', 'softq', 'softr', 'softs', 'softt', 'softu', 'softv', 'softw', 'softx', 'softz',
        'harda', 'hardb', 'hardc', 'hardd', 'harde', 'hardf', 'hardg', 'hardh', 'hardi', 'hardj', 'hardk', 'hardl', 'hardm', 'hardn', 'hardo', 'hardp', 'hardq', 'hardr', 'hards', 'hardt', 'hardu', 'hardv', 'hardw', 'hardx', 'hardz',
        'aminus', 'bminus', 'cminus', 'dminus',
        'aplus', 'bplus', 'cplus', 'dplus',
        'asharp', 'bsharp', 'csharp', 'dsharp', 'esharp', 'fsharp', 'gsharp',
        'anatural', 'bnatural', 'cnatural', 'dnatural', 'enatural', 'fnatural', 'gnatural',
        'aflat', 'bflat', 'cflat', 'dflat', 'eflat', 'fflat', 'gflat',
    }
    word_list = load_word_list(min_score=40).words
    word_list = {word for word in word_list if len(word) >= min_word_length} - banned

    entries = one_ups(word_list, n=1, min_changes=min_changes_per_word, wrapping=False)
    if meta:
        for (i, spelling) in enumerate(spell_meta(meta, entries, max_total_length), 1):
            # len(spelling) = how many words are in this spelling
            # spelling[i] = list of word pairs for the ith position (all equal length)
            # spelling[i][0] = an arbitrary word pair for the ith position
            # spelling[i][0][0] = an arbitrary 'before' word for the ith position
            # len(spelling[i][0][0]) = length of the words in the ith position
            total_len = sum(len(pairs[0][0]) for pairs in spelling)
            print(f"Solution #{i} - length {total_len}")

            for (j, pairs) in enumerate(spelling, 1):
                print(f"    {j}. ", end='')
                for (old, new) in pairs:
                    print(f"{highlight_diffs(old, new)} -> {highlight_diffs(new, old)}, ", end='')
                print("\b\b \b")
            print(flush=True)
    else:
        for (old, new) in entries:
            print(f"{highlight_diffs(old, new)} -> {highlight_diffs(new, old)}", flush=True)

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Process some integers related to word changes."
    )

    parser.add_argument('--min-word-length', type=int, default=1, help='Minimum length of a word')
    parser.add_argument('--max-total-length', type=int, default=None, help='Maximum total length allowed')
    parser.add_argument('--min-changes-per-word', type=int, default=1, help='Minimum number of changes per word')
    parser.add_argument('--meta', type=str, default=None, help='Meta string to spell out')

    args = parser.parse_args()
    return args

def highlight_diffs(s1, s2):
    s = ''
    for (c1, c2) in zip(s1, s2):
        s += c1.lower() if c1 == c2 else c1.upper()
    return s

################################################################################

from collections import defaultdict

def one_off(words, min_diff, max_diff):
    """
    Generate pairs (w1, w2) from a set of words such that:
      - w1 and w2 have the same length.
      - For each position i, either w2[i] == w1[i] or w2[i] == chr(ord(w1[i]) + 1).
      - The total number of positions where w2 differs from w1 (i.e. increments)
        is at least 1 and within the bounds specified by min_diff and max_diff
        (if provided).

    Parameters:
      words   : A set of normalized words (lowercase, punctuation removed).
      min_diff: Minimum number of positions that must be different (or None for no lower bound).
      max_diff: Maximum number of positions that can be different (or None for no upper bound).

    Yields:
      Tuples (w1, w2) that satisfy the "one apart" condition. Each pair is yielded only once.
    """

    # Group words by their length so we only compare words that can match.
    words_by_len = defaultdict(set)
    for word in words:
        words_by_len[len(word)].add(word)

    def build_trie(wordset):
        """Build a trie (prefix tree) from the given set of words."""
        trie = {}
        for word in wordset:
            node = trie
            for letter in word:
                node = node.setdefault(letter, {})
            node["_end"] = True
        return trie

    # Build a trie for each length group.
    tries = {length: build_trie(wset) for length, wset in words_by_len.items()}

    def search_trie(node, word, index, diff, candidate):
        """
        Recursively search the trie for words reachable from `word` by, at each position,
        either keeping the same letter or incrementing it (if possible). `diff` is the number
        of increments used so far, and `candidate` accumulates the letters chosen.
        """
        if index == len(word):
            # At the end, if we used at least one increment and the candidate qualifies
            if diff > 0 and ("_end" in node):
                if (min_diff is None or diff >= min_diff) and (max_diff is None or diff <= max_diff):
                    yield candidate
            return

        letter = word[index]
        # Option 1: use the same letter (no increment).
        if letter in node:
            yield from search_trie(node[letter], word, index + 1, diff, candidate + letter)
        # Option 2: use letter+1 (if possible).
        if letter != 'z':  # Cannot increment 'z'
            next_letter = chr(ord(letter) + 1)
            if next_letter in node:
                new_diff = diff + 1
                # If max_diff is specified, only continue if we haven't exceeded it.
                if max_diff is None or new_diff <= max_diff:
                    yield from search_trie(node[next_letter], word, index + 1, new_diff, candidate + next_letter)

    # For each group of words (same length), use the trie to find candidate pairs.
    for length, wset in words_by_len.items():
        trie = tries[length]
        for word in wset:
            # For each word, search for valid candidates in the trie.
            # This search only explores branches that exist in the dictionary.
            for candidate in search_trie(trie, word, 0, 0, ""):
                # To avoid duplicates (e.g. reporting both (w1, w2) and (w2, w1)),
                # yield only when word is lexicographically less than candidate.
                if word < candidate:
                    yield (word, candidate)

if __name__ == '__main__':
    main()

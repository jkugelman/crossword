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

def one_ups(word_list, n=1, min_changes=1, wrapping=False):
    """
    Find all (parent, child) pairs of words in 'word_list' such that 'child'
    can be formed by incrementing some subset of letters in 'parent' by 'n'.
    At least 'min_changes' letters must differ. If 'wrapping' is True, we allow
    wrap-around (e.g. 'z' -> 'a' if n=1).
    Returns a list of (parent, child) pairs.
    """
    # Ensure we have a set for faster membership checking (if user passes list)
    word_set = set(word_list)

    # Group words by length, because incrementing letters does not change length.
    length_map = defaultdict(list)
    for w in word_set:
        length_map[len(w)].append(w)

    # Build a separate Trie for each length
    trie_map = {}
    for length, words_of_that_length in length_map.items():
        trie_map[length] = build_trie(words_of_that_length)

    # This helper function will convert a child letter 'c' back to a possible parent letter.
    # We want to check if the parent letter could be c, or c - n (mod 26 if wrapping).
    def possible_parent_chars(c):
        """Return [same_char, decremented_char] if valid, otherwise just [same_char]."""
        parents = [c]  # The 'no-change' option
        # Compute c - n (with or without wrapping)
        ord_c = ord(c) - ord('a')  # 0-based letter index
        if wrapping:
            dec_index = (ord_c - n) % 26
        else:
            dec_index = ord_c - n
        if 0 <= dec_index < 26:
            parents.append(chr(dec_index + ord('a')))
        return parents

    results = []

    def dfs_search(child_word, trie_root):
        """
        For a given 'child_word', we want to find all valid 'parent' words in the trie.
        We do a DFS over the trie, branching on either 'same char' or 'char-n'.

        We'll track how many changes we've made so far.
        """
        found_parents = []
        path_chars = []  # to reconstruct the parent word as we go

        def dfs(node, index, changes_so_far):
            if index == len(child_word):
                # Reached the end of child_word; check if node corresponds to a valid word
                if node.is_word and changes_so_far >= min_changes:
                    parent_candidate = "".join(path_chars)
                    found_parents.append(parent_candidate)
                return

            c_child = child_word[index]
            # Gather possible parent chars for c_child
            parents_for_this_char = possible_parent_chars(c_child)

            for p_char in parents_for_this_char:
                child_or_same = (p_char == c_child)  # was this an increment or not?

                if p_char in node.children:
                    # Choose p_char, move deeper
                    path_chars.append(p_char)

                    # If p_char is different from c_child - n, it means no increment (p_char == c_child).
                    # If p_char != c_child, that means p_char == (c_child-n) -> an increment.
                    if child_or_same:
                        # No increment at this position
                        dfs(node.children[p_char], index + 1, changes_so_far)
                    else:
                        # We had an increment at this position
                        dfs(node.children[p_char], index + 1, changes_so_far + 1)

                    path_chars.pop()

        dfs(trie_root, 0, 0)
        return found_parents

    # Collect all (parent, child) pairs
    all_pairs = []
    for w in word_set:
        length_w = len(w)
        if length_w not in trie_map:
            # No trie for this length => skip
            continue

        trie_root = trie_map[length_w]
        # We interpret w as the "child" and look for valid "parents"
        parents = dfs_search(w, trie_root)

        # For each parent p, we have p -> w if p != w in at least min_changes positions
        # (The DFS logic already enforced min_changes, so just filter out exact duplicates)
        for p in parents:
            if p != w:
                all_pairs.append((p, w))

    return all_pairs

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False

def build_trie(words):
    """
    Build a Trie from the given iterable of words.
    Returns the root TrieNode.
    """
    root = TrieNode()
    for w in words:
        node = root
        for c in w:
            if c not in node.children:
                node.children[c] = TrieNode()
            node = node.children[c]
        node.is_word = True
    return root

################################################################################

def spell_meta(meta, entry_pairs, max_total_length=None):
    entries_by_diff_len = group_by_multi(entry_pairs, keys=[
        lambda pair: letter_diff(*pair),
        lambda pair: len(pair[0]),
    ])
    entries_by_len_diff = group_by_multi(entry_pairs, keys=[
        lambda pair: len(pair[0]),
        lambda pair: letter_diff(*pair),
    ])

    return spell_meta_impl(meta, entries_by_diff_len, entries_by_len_diff, max_total_length)

def spell_meta_impl(meta, entries_by_diff_len, entries_by_len_diff, max_total_length):
    # print(f"spell_meta_impl(meta={meta}, max_total_length={max_total_length})")

    # Exact match.
    if meta in entries_by_diff_len:
        for (length, entries) in entries_by_diff_len[meta].items():
            if length <= max_total_length:
                yield [entries]

    # Prefix and suffix and recurse.
    for p in range(1, len(meta)):
        for (length, prefix_entries) in entries_by_diff_len[meta[:p]].items():
            # print(f" p={p}, length={length}, prefix_entries={prefix_entries}")
            if length * 2 > max_total_length:
                continue
            for s in range(1, len(meta) - p + 1):
                suffix_entries = entries_by_len_diff[length][meta[p:][-s:]]
                if not suffix_entries:
                    continue
                # print(f" p={p}, s={s}, length={length}, prefix_entries={prefix_entries}, suffix_entries={suffix_entries}")
                if p + s == len(meta):
                    yield [prefix_entries, suffix_entries]
                    continue
                for spelling in spell_meta_impl(meta[p:][:-s], entries_by_diff_len, entries_by_diff_len, max_total_length - length * 2):
                    yield [prefix_entries, *spelling, suffix_entries]

def letter_diff(old, new):
    return ''.join(o for (o, n) in zip(old, new) if o != n)

def group_by_multi(iterable, keys):
    def nested_dict_factory(depth):
        if depth == 1:
            return []
        else:
            return defaultdict(lambda: nested_dict_factory(depth - 1))

    if not keys:
        raise ValueError("At least one key function must be provided.")

    nested = defaultdict(lambda: nested_dict_factory(len(keys)))

    for value in iterable:
        current = nested
        for key_func in keys:
            current = current[key_func(value)]
        current.append(value)

    return nested

if __name__ == '__main__':
    main()

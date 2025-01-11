#!/usr/bin/env python3

# Finds entries where <min_changes> letters can be incremented by <n> to become a different entry.

import argparse
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import product
from pygtrie import CharTrie
import sys

from merge import *

def main():
    args = parse_arguments()

    min_word_length = args.min_word_length
    max_total_length = args.max_total_length
    min_changes_per_word = args.min_changes_per_word
    meta = args.meta

    word_list = load_word_list(min_score=40).words
    word_list = {word for word in word_list if len(word) >= min_word_length}

    entries = one_ups(word_list, n=1, min_changes=min_changes_per_word, wrapping=False)
    if meta:
        for (i, spellings) in enumerate(spell_meta(meta, entries, max_total_length)):
            print(f"Solution #{i+1} - length {sum(len(old) for (old, new) in spellings)}")
            for (old, new) in spellings:
                print(f"{highlight_diffs(old, new)} -> {highlight_diffs(new, old)}")
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

def spell_meta(meta, entries, max_total_length=None):
    """
    Build 'meta' from the changed letters of (before, after) pairs under these conditions:
      1) No real pair is reused in the same solution.
      2) The concatenation of changed-letter tokens exactly equals 'meta'.
      3) The sequence of 'before' lengths is palindromic.
      4) The total sum of all 'before' lengths does not exceed 'max_total_length'
         (if provided).

    Returns: A list of final solutions, where each solution is a list
             of (before, after) pairs in the order they appear to form 'meta'.
    """

    # 1) Precompute changed letters for each entry
    pre_data = []
    for bef, aft in entries:
        if len(bef) != len(aft):
            continue  # skip if mismatched
        changed_positions = []
        for i in range(len(bef)):
            if bef[i] != aft[i]:
                changed_positions.append(i)
        diff_str = "".join(bef[i] for i in changed_positions)
        pre_data.append({
            "before": bef,
            "after": aft,
            "token": diff_str,
            "length": len(bef),
        })

    # 2) Collapse by (token, length).
    collapsed_map = defaultdict(list)
    for item in pre_data:
        key = (item["token"], item["length"])
        collapsed_map[key].append((item["before"], item["after"]))

    collapsed_data = []
    for (token, length), pairs_list in collapsed_map.items():
        collapsed_data.append({
            "token": token,
            "length": length,
            "pairs": pairs_list  # all real pairs that share (token, length)
        })

    n = len(meta)

    # 3) Memoized search over (index, usage_counts, current_length_sum).
    #    usage_counts[i] = how many times we've used collapsed_data[i].
    #    current_length_sum = sum of all 'length' used so far.

    @lru_cache(None)
    def backtrack(index, usage_counts, current_length_sum):
        """
        :param index: current position in 'meta' (0-based)
        :param usage_counts: tuple of integers for each index in collapsed_data
        :param current_length_sum: the total sum of 'before' lengths used so far
        :return: a list of partial solutions (each is a list of collapsed_data indices)
        """
        if index == n:
            # matched the entire meta string
            return [[]]  # one valid "empty" extension

        solutions_here = []
        usage_list = list(usage_counts)

        for i, entry in enumerate(collapsed_data):
            # Check if we have capacity to use this group again
            if usage_list[i] >= len(entry["pairs"]):
                continue  # we've run out of real pairs in this group

            token = entry["token"]
            length_i = entry["length"]

            # Prune if adding this length would exceed max_total_length
            new_length_sum = current_length_sum + length_i
            if max_total_length is not None and new_length_sum > max_total_length:
                continue

            # Check if the token matches meta at 'index'
            if meta.startswith(token, index):
                # Use it
                usage_list[i] += 1
                sub_solutions = backtrack(index + len(token),
                                          tuple(usage_list),
                                          new_length_sum)
                # sub_solutions are lists of collapsed indices from the next position onward
                for sol in sub_solutions:
                    solutions_here.append([i] + sol)
                usage_list[i] -= 1

        return solutions_here

    # Collect all solutions ignoring the palindrome check
    initial_usage = tuple([0]*len(collapsed_data))
    raw_solutions = backtrack(0, initial_usage, 0)

    # 4) Filter those whose length sequence is palindromic
    palindromic_solutions_collapsed = []
    for sol in raw_solutions:
        length_seq = [collapsed_data[idx]["length"] for idx in sol]
        if length_seq == length_seq[::-1]:
            palindromic_solutions_collapsed.append(sol)

    # 5) Expand each collapsed solution into all possible real (before, after) combos.
    from itertools import permutations, product
    expanded_solutions = []
    for sol in palindromic_solutions_collapsed:
        # Count how many times each collapsed idx is used
        from collections import Counter
        usage_counter = Counter(sol)

        # Build all expansions by picking distinct real pairs for each usage
        index_to_combos = {}
        valid_solution = True
        for idx_used, times_used in usage_counter.items():
            all_real_pairs = collapsed_data[idx_used]["pairs"]
            # We must pick 'times_used' distinct pairs from this list
            if len(all_real_pairs) < times_used:
                valid_solution = False
                break
            # Permutations since order matters in the final sequence
            index_to_combos[idx_used] = list(permutations(all_real_pairs, times_used))

        if not valid_solution:
            continue

        # Cartesian product across each index's permutations
        all_keys = list(usage_counter.keys())
        combos_lists = [index_to_combos[k] for k in all_keys]
        for combo_selection in product(*combos_lists):
            # combo_selection is a tuple of permutations, one for each key in all_keys
            assignment = {}
            for k_i, chosen_perm in zip(all_keys, combo_selection):
                assignment[k_i] = chosen_perm

            # Reconstruct the final solution in the order given by 'sol'
            usage_in_order = Counter()
            real_solution = []
            for collapsed_idx in sol:
                used_so_far = usage_in_order[collapsed_idx]
                real_pair = assignment[collapsed_idx][used_so_far]
                real_solution.append(real_pair)
                usage_in_order[collapsed_idx] += 1

            expanded_solutions.append(real_solution)

    # 6) De-duplicate final solutions
    unique_solutions = set()
    for sol in expanded_solutions:
        unique_solutions.add(tuple(sol))  # convert list->tuple for hashing
    deduped_solutions = [list(u) for u in unique_solutions]

    return deduped_solutions

if __name__ == '__main__':
    main()

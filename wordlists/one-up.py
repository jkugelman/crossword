#!/usr/bin/env python3

# Finds entries where <min_changes> letters can be incremented by <n> to become a different entry.

from collections import defaultdict
from merge import *
from pygtrie import CharTrie
import sys

def main():
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print(f"Usage: {sys.argv[0]} <min_length> <min_changes> [meta]", file=sys.stderr)
        sys.exit(1)

    min_length = int(sys.argv[1])
    min_changes = int(sys.argv[2])
    meta = sys.argv[3] if len(sys.argv) >= 4 else None

    word_list = load_word_list(min_score=40).words
    word_list = {word for word in word_list if len(word) >= min_length}

    entries = one_ups(word_list, n=1, min_changes=min_changes, wrapping=False)
    if meta:
        for (i, spellings) in enumerate(spell_meta(meta, entries)):
            print(f"Solution #{i+1} - length {sum(len(old) for (old, new) in spellings)}")
            for (old, new) in spellings:
                print(f"{highlight_diffs(old, new)} -> {highlight_diffs(new, old)}")
            print(flush=True)
    else:
        for (old, new) in entries:
            print(f"{highlight_diffs(old, new)} -> {highlight_diffs(new, old)}", flush=True)

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

def spell_meta(meta, entries):
    """
    Exhaustively find all ways to build 'meta' from the *changed letters*
    of a sequence of (before, after) pairs, with these conditions:
      1) No pair is reused in a single solution.
      2) The concatenation of changed-letter tokens exactly equals 'meta'.
      3) The sequence of 'before'-lengths is palindromic.

    :param meta: str, the target to build (e.g. "foobar").
    :param entries: list of (before, after) pairs (each a distinct entry).
    :return: A list of solutions, where each solution is a list of indices or
             a list of dicts describing which entries were used.
    """
    # 1) Precompute the changed letters for each entry
    diff_data = []
    for idx, (bef, aft) in enumerate(entries):
        if len(bef) != len(aft):
            # Should never happen if one_ups pairs them, but just in case
            continue

        changed_positions = []
        for i in range(len(bef)):
            if bef[i] != aft[i]:
                changed_positions.append(i)

        diff_str = "".join(bef[i] for i in changed_positions)

        # If you want to ignore pairs that have no changes, skip if diff_str == ""
        # But maybe you want to include them (they contribute an empty string to meta).
        # For now, we'll keep them, so they can match an empty prefix (which is rarely useful).
        # It's your call to exclude them if needed.

        diff_data.append({
            "diff_str": diff_str,
            "length": len(bef),
            "before": bef,
            "after": aft,
            "index": idx  # original index in 'entries' for reference
        })

    n = len(meta)
    solutions = []

    # 2) Depth-first search / backtracking
    def backtrack(index, used, chosen):
        """
        :param index: how many chars of meta are matched so far
        :param used: set of indices (in diff_data) that we've already used
        :param chosen: list of indices into diff_data of the chosen pairs (in order)
        """
        if index == n:
            # We've matched all of meta. Check symmetry in the chosen lengths
            lengths_seq = [diff_data[i]["length"] for i in chosen]
            if lengths_seq == lengths_seq[::-1]:  # palindrome check
                # Record a valid solution
                solution_pairs = [(diff_data[i]['before'], diff_data[i]['after']) for i in chosen]
                solutions.append(solution_pairs)
            return

        # If we're not at the end, try each diff_data entry that is not used
        for i in range(len(diff_data)):
            if i in used:
                continue
            token = diff_data[i]["diff_str"]
            # If token matches meta[index:] as a prefix...
            if meta.startswith(token, index):
                used.add(i)
                chosen.append(i)
                new_index = index + len(token)

                backtrack(new_index, used, chosen)

                chosen.pop()
                used.remove(i)

    backtrack(0, set(), [])

    return solutions


if __name__ == '__main__':
    main()

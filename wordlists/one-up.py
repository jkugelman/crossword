#!/usr/bin/env python3

# Finds entries where <min_changes> letters can be incremented by <n> to become a different entry.

from collections import Counter, defaultdict
from functools import lru_cache
from itertools import product
from pygtrie import CharTrie
import sys

from merge import *

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
    Build 'meta' from the changed letters of (before, after) pairs
    under these conditions:
      1) No real pair is reused in the same solution.
      2) The concatenation of changed-letter tokens exactly equals 'meta'.
      3) The sequence of 'before' lengths is palindromic.

    This version collapses duplicates so that if multiple real pairs
    share the same (diff_str, length), we treat them as one 'collapsed group'
    during search. Then we expand the collapsed solutions at the end
    and remove duplicates.

    Returns: A list of final solutions, where each solution is a list
             of (before, after) pairs in the order they appear to form 'meta'.
    """

    # 1) Precompute changed letters (diff_str) for each entry.
    #    We'll store an intermediate list of:
    #      {
    #        "before": bef,
    #        "after": aft,
    #        "token": diff_str,
    #        "length": len(bef)
    #      }
    pre_data = []
    for bef, aft in entries:
        if len(bef) != len(aft):
            # skip if somehow mismatched
            continue
        changed_positions = []
        for i in range(len(bef)):
            if bef[i] != aft[i]:
                changed_positions.append(i)
        diff_str = "".join(bef[i] for i in changed_positions)
        pre_data.append({
            "before": bef,
            "after": aft,
            "token": diff_str,
            "length": len(bef)
        })

    # 2) Collapse by (token, length).
    #    We'll build a dict: collapsed_map[(token, length)] -> list of (before, after)
    collapsed_map = defaultdict(list)
    for item in pre_data:
        key = (item["token"], item["length"])
        collapsed_map[key].append((item["before"], item["after"]))

    # Build a list 'collapsed_data' = [
    #   {
    #     "token": ...,
    #     "length": ...,
    #     "pairs": [... list of (before, after) ...]
    #   },
    #   ...
    # ]
    # This is easier to work with than a dict.
    collapsed_data = []
    for (token, length), pairs_list in collapsed_map.items():
        collapsed_data.append({
            "token": token,
            "length": length,
            "pairs": pairs_list  # a list of distinct real (bef, aft)
        })

    # We'll need a quick way to see how many total 'copies' are available
    # for each collapsed entry. That is simply len(pairs).
    # No solution can use a single collapsed entry more times than
    # the number of real pairs in that group.

    # 3) Search (left-to-right) for ways to form 'meta' from the tokens
    #    of these collapsed groups. We must also enforce "no reuse beyond available count"
    #    and do a final palindrome check on lengths.

    n = len(meta)

    # We'll store partial results in a memo:
    #   memo[(index, usage_counts_tuple)] = a list of solutions (in collapsed indices)
    # That is, if we are at position 'index' in meta, and we have used each collapsed entry
    # some number of times, the result is all possible ways to finish building meta[index:].
    #
    # usage_counts_tuple is a tuple of how many times we've used each index in 'collapsed_data'.
    # Because we can't exceed collapsed_data[i]["pairs"] in usage (i.e. usage_counts[i] <= len(pairs)).

    @lru_cache(None)
    def backtrack(index, usage_counts):
        """
        :param index: current position in 'meta'
        :param usage_counts: a tuple the same length as collapsed_data,
                             where usage_counts[i] tells how many times
                             we've used collapsed_data[i].
        :return: A list of partial solutions (each a list of collapsed_data indices),
                 ignoring palindrome checks here. We'll do that after collecting all.
        """
        if index == n:
            # matched all of meta
            return [[]]  # one "empty" way to finish

        solutions_here = []
        usage_counts_list = list(usage_counts)

        # Try each collapsed entry i
        for i, entry in enumerate(collapsed_data):
            token = entry["token"]
            length_i = entry["length"]
            # If we've already used it usage_counts_list[i] times,
            # can we still use it again? We can't exceed len(entry["pairs"]).
            if usage_counts_list[i] >= len(entry["pairs"]):
                continue  # no more available real pairs in that group

            # Check if token matches meta at 'index' as a prefix
            if meta.startswith(token, index):
                # We can use it
                usage_counts_list[i] += 1
                new_index = index + len(token)

                sub_solutions = backtrack(new_index, tuple(usage_counts_list))
                # sub_solutions is a list of solutions from new_index onward
                # Each sub_solution is a list of collapsed indices
                for sol in sub_solutions:
                    solutions_here.append([i] + sol)

                # revert
                usage_counts_list[i] -= 1

        return solutions_here

    # Collect all solutions ignoring palindrome
    initial_usage = tuple([0]*len(collapsed_data))
    raw_solutions = backtrack(0, initial_usage)

    # 4) Now filter those whose length sequence is palindromic.
    #    For each solution, we convert from collapsed indices to their lengths,
    #    then check if it's a palindrome. If so, keep it.
    palindromic_solutions_collapsed = []
    for sol in raw_solutions:
        length_seq = [collapsed_data[idx]["length"] for idx in sol]
        if length_seq == length_seq[::-1]:
            palindromic_solutions_collapsed.append(sol)

    # 5) Expand each collapsed solution into ALL possible real (before, after) combos.
    #    For example, if the collapsed solution = [i1, i2, i2, i3],
    #    that means we used collapsed_data[i1] once, collapsed_data[i2] twice, collapsed_data[i3] once.
    #
    #    We'll produce all ways to pick a distinct real pair for each usage of i2, etc.
    #    Then we'll end up with final sequences of (before, after).

    expanded_solutions = []
    for sol in palindromic_solutions_collapsed:
        # Example sol = [i1, i2, i2, i3]
        # We need to gather them by consecutive usage. Let's build a structure:
        #   usage_order = [(i1, 1), (i2, 2), (i3, 1)]  or rather a direct sequence.

        # We'll build a list of "options for each step", e.g.
        #   step_options = [ list_of_real_pairs_for_i1, list_of_real_pairs_for_i2, ..., list_of_real_pairs_for_i3 ]
        # But we must ensure that if i2 appears multiple times, we pick distinct real pairs each time.

        # Approach: we'll just do it step-by-step, ensuring distinct usage in the final result.
        # A simpler approach: do a single pass building the final expansions.

        # 1) Count how many times each collapsed index i appears in 'sol'
        usage_counter = Counter(sol)  # e.g. { i2: 2, i1: 1, i3: 1, ... }

        # 2) For each i in usage_counter, we must choose usage_counter[i] distinct real pairs
        #    from collapsed_data[i]["pairs"].
        #    We'll compute all combinations of size usage_counter[i] among that list.
        #    Then in the actual solution order, we place them in the positions that used i.

        # We'll gather all combination sets first
        index_to_combos = {}
        for i, times_used in usage_counter.items():
            all_real_pairs = collapsed_data[i]["pairs"]
            if len(all_real_pairs) < times_used:
                # impossible to choose distinct real pairs
                index_to_combos[i] = []
            else:
                # from all_real_pairs, choose 'times_used' distinct ones in *combinations*
                # but order might matter because the positions might appear in different places in 'sol'.
                #
                # Actually, to produce *all permutations* that fill those positions,
                # we must pick combinations then consider permutations. Or simpler: pick permutations of length times_used.
                from itertools import permutations
                index_to_combos[i] = list(permutations(all_real_pairs, times_used))

        # If any index has zero combos, that solution can't expand
        for i in usage_counter:
            if not index_to_combos[i]:
                # means no expansions
                break
        else:
            # If we didn't break, that means we have expansions for each index
            # We do a big cartesian product across index_to_combos[i] for each i in usage_counter.
            # e.g. if i2 -> 2 combos, i1 -> 3 combos, we do the product of those sets
            # Then we fill them in the appropriate places.
            all_keys = list(usage_counter.keys())
            combos_lists = [index_to_combos[k] for k in all_keys]  # list of lists-of-permutations
            for combo_selection in product(*combos_lists):
                # combo_selection is a tuple of chosen permutations for each key in all_keys
                # e.g. ( perm_for_i1, perm_for_i2, ... )
                # Now we place them in the final order as in 'sol'

                # Build a dict i -> the chosen permutation (one from combos_lists).
                assignment = {}
                for k_i, chosen_perm in zip(all_keys, combo_selection):
                    assignment[k_i] = chosen_perm

                # Now we reconstruct the final solution in the order given by 'sol'
                # e.g. if sol=[i2, i1, i2, i3], we pick the first element from assignment[i2], then assignment[i1], ...
                # We must track how many items from assignment[i2] we have used so far.
                usage_counters_for_build = Counter()
                real_solution = []
                for collapsed_idx in sol:
                    used_count_so_far = usage_counters_for_build[collapsed_idx]
                    real_pair = assignment[collapsed_idx][used_count_so_far]
                    real_solution.append(real_pair)
                    usage_counters_for_build[collapsed_idx] += 1

                expanded_solutions.append(real_solution)

    # 6) De-duplicate final solutions (because different permutations or different
    #    combo_selection might produce the same final arrangement).
    #    We'll just do a set of tuples:
    unique_solutions = set()
    for sol in expanded_solutions:
        # sol is a list of (before, after) pairs
        # convert to a tuple-of-tuples for hashing
        unique_solutions.add(tuple(sol))

    # Convert back to a list of lists
    deduped_solutions = [list(u) for u in unique_solutions]

    return deduped_solutions


if __name__ == '__main__':
    main()

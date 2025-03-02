#!/usr/bin/env python3

# Find words that are valid entries without the end letters,
# and where those letters spell out two meta answers. For example:
#
# fries + rolls: flatter / relleno / ifatall / earcanal / snapless (7/7/7/8/8)

from merge import load_word_list
import re
import sys

def main():
    words = set(load_word_list(min_score=40).words.keys())
    words = {word for word in words if len(word) >= 6 and word[1:-1] in words}
    words = {word for word in words if not re.search('[^s]s$', word)}

    metas = set(sys.argv[1:])

    for meta1, meta2, combo in spell_metas(words, metas):
        print(f"{meta1} + {meta2}: {' / '.join(combo)} ({'/'.join(str(len(c)) for c in combo)})", flush=True)

def spell_metas(words, metas):
    # Precompute a dictionary mapping (first_letter, last_letter) -> list of words.
    letter_pair_dict = {}
    for word in words:
        key = (word[0], word[-1])
        letter_pair_dict.setdefault(key, []).append(word)

    # Iterate over every ordered pair of meta words
    for meta1 in metas:
        for meta2 in metas:
            if meta1 == meta2:
                continue
            if len(meta1) != len(meta2):
                continue
            L = len(meta1)

            # Build candidate lists: for each position, the candidate words
            # must have first letter meta1[i] and last letter meta2[i].
            candidates = []
            valid = True
            for i in range(L):
                key = (meta1[i], meta2[i])
                # Get words matching the key and exclude if they are equal to either meta word.
                cand = [w for w in letter_pair_dict.get(key, [])
                        if w != meta1 and w != meta2]
                if not cand:
                    valid = False
                    break
                candidates.append(cand)
            if not valid:
                continue

            # Backtracking routine to select one candidate word from each list ensuring distinctness.
            def backtrack(i, combo):
                if i == L:
                    yield (meta1, meta2, combo)
                    return
                for w in candidates[i]:
                    if w in combo:
                        continue
                    yield from backtrack(i + 1, combo + [w])

            yield from backtrack(0, [])

if __name__ == '__main__':
    main()

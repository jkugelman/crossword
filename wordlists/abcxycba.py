#!/usr/bin/env python3

from collections import defaultdict
from merge import *

def find_matching_pairs(wordlist):
    # Preprocess words to create a dictionary of `b[1:]`
    suffix_dict = defaultdict(list)
    for b in wordlist:
        suffix_dict[b[1:]].append(b)
        suffix_dict[b[2:]].append(b)

    # Find pairs where a[:-1] matches b[1:]
    pairs = []
    for a in wordlist:
        if len(a) < 4: continue

        prefix = a[:-1][::-1]
        if prefix in suffix_dict:
            for b in suffix_dict[prefix]:
                if a == b[::-1]:
                    continue
                pairs.append((a, b))

    pairs.sort(key=lambda w: (len(w[0]), w))
    return pairs

# Example usage
wordlist = load_word_list(min_score=30).words
result = find_matching_pairs(wordlist)
for a, b in result:
    print(f"{a} {b}")

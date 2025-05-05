#!/usr/bin/env python3

from itertools import combinations

from lib import grouped_by_len, load_words

def main():
    words = load_words()

    # Nothing at all at 17+.
    # Nothing interesting at 15-16.
    if False:
        jumpers(words, max_length=14, pivot_length=2, min_prefix=3, min_suffix=3)

    # Nothing at all at 13+.
    if True:
        jumpers(words, max_length=12, pivot_length=3, min_prefix=3, min_suffix=3)

def jumpers(words, max_length, pivot_length, min_prefix, min_suffix):
    words_by_len = grouped_by_len(words)

    for length in sorted(words_by_len, reverse=True):
        if length > max_length:
            continue

        for pivot in range(min_prefix - 1, length - (pivot_length - 1) - (min_suffix - 1)):
            print(f"length={length}, pivot={pivot}", flush=True)

            for clued_a, clued_b in combinations(words_by_len[length], 2):
                # Pivot strings must be equal, when reversed.
                if clued_a[pivot:pivot+pivot_length] != clued_b[pivot:pivot+pivot_length][::-1]:
                    continue

                # The beginnings can't be the same.
                if clued_a[:pivot+pivot_length] == clued_b[:pivot+pivot_length]:
                    continue

                # The ends can't be the same.
                if clued_a[pivot:] == clued_b[pivot:]:
                    continue

                # The two words in the grid must be real words.
                gridded_a = clued_a[:pivot+1] + clued_b[pivot+pivot_length:]
                if gridded_a not in words:
                    continue
                gridded_b = clued_b[:pivot+1] + clued_a[pivot+pivot_length:]
                if gridded_b not in words:
                    continue

                # The overall score is the lowest of all four words.
                score = min(words[clued_a], words[clued_b], words[gridded_a], words[gridded_b])

                # Show the find.
                print(f"    {gridded_a} ({score})")
                if pivot_length <= 2:
                    print(f"    {' ' * pivot}|")
                else:
                    for i in range(1, pivot_length-1):
                        print(f"    {' ' * pivot}{clued_a[pivot+i]}")
                print(f"    {gridded_b}")
                print()

if __name__ == '__main__':
    main()

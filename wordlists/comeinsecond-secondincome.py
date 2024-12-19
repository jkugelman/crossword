#!/usr/bin/env python3

from merge import *

def main():
    word_list = load_word_list()

    for (left, right) in find_swappable_words(word_list.words.keys()):
        print(f"{'|'.join(left)} <--> {'|'.join(right)}")

def find_swappable_words(word_list):
    min_len = 1

    for word in word_list:
        if len(word) < 6:
            continue
        for i in range(1, len(word) - 1):
            for j in range(i + 1, len(word) - 0):
                parts = word[:i], word[i:j], word[j:]
                a, b, c = parts

                if any(len(p) < min_len for p in parts):
                    continue
                if sum(1 for p in parts if len(p) == 1) > 1:
                    continue
                # No duplicates
                if len(set(parts)) != len(parts):
                    continue

                swapped = c + b + a
                if word > swapped:
                    continue
                if word == swapped:
                    continue
                if swapped in word_list:
                    yield (a, b, c), (c, b, a)

if __name__ == '__main__':
    main()

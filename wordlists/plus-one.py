#!/usr/bin/env python3

# Finds entries where 3+ letters can be incremented by one to become a different entry.
# Or, more generally, where <min_length> letters can be incremented by <n>.

from merge import *
import sys

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <n> <min_length>", file=sys.stderr)
        sys.exit(1)

    n = int(sys.argv[1])
    min_length = int(sys.argv[2])
    word_list = load_word_list(min_score=40).words

    for (left, old, new, right) in plus_one(word_list, n, min_length):
        #print(f"{left}{old}{right} -> {left}{new}{right} ({left}[{old}]{right} -> {left}[{new}]{right})", flush=True)
        print(f"{left}[{old}]{right} -> {left}[{new}]{right}", flush=True)

def plus_one(word_list, n, min_length):
    results = []

    for word in word_list:
        for start in range(len(word) - (min_length - 1)):
            for length in range(min_length, len(word) - start + 1):
                # Extract the substring to increment
                old = word[start:start + length]
                new = ''.join(chr((ord(c) - 96 + n) % 26 + 96) if 'a' <= c <= 'z' else c for c in old)

                # Create the modified word
                candidate = word[:start] + new + word[start + length:]

                # Check if the modified word exists
                if candidate in word_list:
                    yield (word[:start], old, new, word[start + length:])

if __name__ == '__main__':
    main()

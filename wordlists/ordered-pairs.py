#!/usr/bin/env python3

# Find words with "ordered pairs" -- a substring followed by the same letters sorted.
# For Tarun Krishnamurthy.

import re
import sys

def main():
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <wordlist.txt> <minscore> <len>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    min_score = int(sys.argv[2])
    length = int(sys.argv[3])

    word_list = load_word_list(path)

    for word, score in word_list.items():
        if score < min_score:
            continue
        for i in range(len(word) - length*2 + 1):
            l = word[:i]
            a = word[i:i+length]
            b = word[i+length:i+length*2]
            r = word[i+length*2:]

            if list(sorted(a)) == list(b) and a != b:
                print(f"{l}[{a.upper()}][{b.upper()}]{r}", flush=True)

def load_word_list(path):
    with open(path) as file:
        words = dict()

        for line in file:
            word, score = line.split(';', 1)
            word = re.sub('[^a-z]', '', word.lower())
            score = int(score.split(';')[0])
            words[word] = score

        return words

if __name__ == '__main__':
    main()

#!/usr/bin/env python3

# Interweave two company names to form a word?
# Lance's idea.

from lib import load_words

def main():
    words = load_words()
    companies = {line.strip() for line in open('companies.txt')}

    for word in words:
        if len(word) < 6:
            continue

        a = word[::2]
        b = word[1::2]
        if a in companies and b in companies:
            print(f"{a} + {b} = {word}", flush=True)

if __name__ == '__main__':
    main()

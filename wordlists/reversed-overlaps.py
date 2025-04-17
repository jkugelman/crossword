#!/usr/bin/env python3

from collections import defaultdict

from lib import load_words

def main():
    words = load_words(min_score=40)
    for pair in reversed_overlaps(words):
        print(pair)

def reversed_overlaps(words):
    root = TrieNode()
    n = 5

    # Step 1: Build the trie with reversed words
    for word in words:
        reversed_word = word[::-1]
        insert_into_trie(root, reversed_word, word, n)

    # Step 2: Check suffixes against the trie
    for word in words:
        for i in range(len(word) - n + 1):
            suffix = word[i:]
            matches = find_in_trie(root, suffix)
            for match in matches:
                if len(word) < 8 or len(match) < 8:
                    continue
                if word[-7] == match[-7] and word < match:
                    yield (
                        word[:-7] + word[-7].upper() + word[-6:],
                        match[:-7] + match[-7].upper() + match[-6:],
                    )

class TrieNode:
    def __init__(self):
        self.children = {}
        self.words = set()

def insert_into_trie(root, reversed_word, original_word, n):
    node = root
    for i, char in enumerate(reversed_word):
        node = node.children.setdefault(char, TrieNode())
        if i + 1 >= n:
            node.words.add(original_word)

def find_in_trie(root, suffix):
    node = root
    for char in suffix:
        if char not in node.children:
            return set()
        node = node.children[char]
    return node.words

# Example usage
if __name__ == '__main__':
    main()

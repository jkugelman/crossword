#!/usr/bin/env python3

# Finds two-word phrases where both words are synonyms of the words in another two-word phrase.
# Example: canoodles = buttloads, automate = carpal

from itertools import product
from nltk.corpus import wordnet as wn
from pprint import pprint

from merge import load_word_list

def main():
    words = load_word_list(min_score=30).words
    min_len = 3

    for word in words:
        # print(f"\r\033[2K{word}", end='', flush=True)

        for i in range(min_len, len(word) - min_len + 1):
            left, right = word[:i], word[i:]
            if left not in words or right not in words:
                continue
            if left == right:
                continue
            multi_synonyms = set(multi_synonym(words, [left, right]))
            if multi_synonyms:
                # print("\r\033[2K", end='')
                print(f"{left} {right} = {', '.join(multi_synonyms)}", flush=True)

def get_synonyms(word):
    """Retrieve synonyms for a word using WordNet."""
    synonyms = set()
    for synset in wn.synsets(word):
        for lemma in synset.lemmas():
            synonyms.add(lemma.name().replace('_', '').lower())

    # Remove the word and its singular/plural.
    synonyms.discard(word)
    synonyms.discard(word + 's')
    if word.endswith('s'):
        synonyms.discard(word[:-1])

    return synonyms

def multi_synonym(dictionary, words):
    """Find dictionary entries that can be formed by concatenating synonyms of words."""
    # Precompute synonyms for each word in `words`
    synonym_lists = [get_synonyms(word) for word in words]

    # Generate all possible concatenated words from synonyms
    candidates = set(product(*synonym_lists))

    for combo in candidates:
        if ''.join(combo) in dictionary:
            yield ' '.join(combo)

if __name__ == '__main__':
    main()

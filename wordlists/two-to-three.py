#!/usr/bin/env python3

# Playing around with two-word phrases that can be turned into three-word phrases.

import sys

from merge import load_word_list
from phrases import phrases as find_phrases

def main():
    words = prepare_words()

    # print_two_to_three(words)
    print_phrases_with_spanners(words)

def print_two_to_three(words):
    """
    Prints two-word phrases that can be parsed as three-word phrases.
    """
    for word in sorted(words):
        phrases = [tuple(phrase) for phrase in find_phrases(word, words)]

        p2s = {p2 for p2 in phrases if len(p2) == 2}
        if not p2s:
            continue

        p3s = {p3 for p3 in phrases if len(p3) == 3
               if not all(
                   p3[0] == p2[0] or p3[2] == p2[1] or
                   p3[0] + p3[1] == p2[0] or p3[1] + p3[2] == p2[1]
                   for p2 in p2s
               )}
        if not p3s:
            continue

        print(f"{word} = {', '.join(' '.join(p3) for p3 in p3s)}", flush=True)

def print_phrases_with_spanners(words):
    """
    Prints two-word phrases with a hidden middle word.
    """
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <min_span> <min_length>", file=sys.stderr)
        sys.exit(1)

    min_span = int(sys.argv[1])
    min_length = int(sys.argv[2])

    for word in sorted(words):
        phrases = [tuple(phrase) for phrase in find_phrases(word, words)]

        p2s = {p2 for p2 in phrases if len(p2) == 2}
        if not p2s:
            continue

        for w1, w2 in p2s:
            for spanner in hidden_spanners(words, w1, w2, min_span, min_length):
                print(f"{w1} {spanner} {w2}", flush=True)

def hidden_spanners(words, w1, w2, min_span, min_length):
    """
    Finds all words in 'words' that can be formed by combining a suffix of w1 and a prefix of w2.

    Parameters:
        words (set or dict): A collection of words to check against.
        w1 (str): The first word.
        w2 (str): The second word.
        min_span (int): Minimum number of characters to take from both w1 and w2.
        min_length (int): Minimum total length for the hidden spanning word.

    Returns:
        set: A set of hidden words that span w1 and w2.
    """
    spanners = set()
    # Loop over possible lengths for the suffix from w1 and prefix from w2
    for i in range(min_span, len(w1)):
        for j in range(min_span, len(w2)):
            if i + j < min_length:
                continue
            candidate = w1[-i:] + w2[:j]
            if candidate in words:
                spanners.add(candidate)
    return spanners

def prepare_words():
    words = load_word_list(min_score=40).words

    # Filter out short words.
    words = {word for word, score in words.items() if len(word) >= 3}

    # Filter out ugly words.
    words -= {
        'aba',
        'aca',
        'ach',
        'acte',
        'acti',
        'actin',
        'activ',
        'ade',
        'ades',
        'adv',
        'aero',
        'cert',
        'dah',
        'dal',
        'dit',
        'dona',
        'edt',
        'edu',
        'een',
        'ent',
        'ents',
        'erg',
        'erm',
        'ers',
        'ess',
        'est',
        'fri',
        'gma',
        'gro',
        'hana',
        'ican',
        'ile',
        'iles',
        'ing',
        'inga',
        'lan',
        'oni',
        'onit',
        'ons',
        'ors',
        'ost',
        'ows',
        'rbs',
        'rds',
        'res',
        'rica',
        'rican',
        'ricans',
        'ssa',
        'sts',
        'tbar',
        'tbars',
        'tem',
        'ting',
        'ural',
    }

    return words

if __name__ == '__main__':
    main()

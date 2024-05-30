#!/usr/bin/env python3

import itertools
import pronouncing
import re

import merge

def main():
    word_list = merge.load_word_list(min_score=30)
    word_list = word_list.words.keys()

    # word_list = {'propaganda', 'pocahontas'}

    for entry in word_list:
        for phones in pronouncing.phones_for_word(entry):
            phones = phones.split()
            if phones[-1] != 'AH0':
                continue

            for split_points in powerset(find_split_points(phones)):
                # Make sure there are at least two -a words.
                if len(split_points) < 1:
                    continue

                split_phones = split_at_indices(phones, split_points)

                # Don't just use the word "a".
                if ['AH0'] in split_phones:
                    continue

                # Change -a to -er.
                split_phones = [change_endings(phones) for phones in split_phones]

                # Convert the phones back into words and abort if they're not all words.
                er_words = [pronouncing.search('^' + re.sub(r'\d', r'\\d', ' '.join(phones)) + '$') for phones in split_phones]

                for er_words in itertools.product(*er_words):
                    print(f"{entry} -> {' '.join(er_words)}", flush=True)

def find_split_points(input_list):
    split_points = []

    # Iterate over the list to find split points
    for i in range(len(input_list) - 1):
        if input_list[i] == 'AH0':
            split_points.append(i + 1)  # Split after 'AH0'
        if input_list[i] == 'AH0' and input_list[i + 1] in {'S', 'Z'}:
            split_points.append(i + 2)  # Split after 'AH0', 'S' and 'AH0', 'Z'

    return sorted(set(split_points))  # Sort and remove duplicates


def split_at_indices(input_list, indices):
    # Ensure indices are sorted
    sorted_indices = sorted(indices)

    # Initialize variables
    sublists = []
    start = 0

    # Split the list at each index
    for index in sorted_indices:
        if index < len(input_list):
            sublists.append(input_list[start:index])
            start = index

    # Add the last segment of the list
    sublists.append(input_list[start:])

    return sublists

def powerset(iterable):
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s) + 1))

def change_endings(phones):
    if ends_with(phones, ['AH0']):
        return phones[:-1] + ['ER0']
    elif ends_with(phones, ['AH0', 'S']):
        return phones[:-2] + ['AH0', 'Z']
    else:
        return phones

def ends_with(a, b):
    if len(b) > len(a):
        return False

    return a[-len(b):] == b

if __name__ == '__main__':
    main()

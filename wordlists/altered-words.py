#!/usr/bin/env python3

import argparse
import sys

from lib import load_words, phrases

def main():
    alterers = {
        'semordnilap': semordnilap,
        'beheaded': beheaded,
        'curtailed': curtailed,
        'inside_out': inside_out,
        'front_to_back': front_to_back,
        'back_to_front': back_to_front,
    }

    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('alterer', choices=alterers.keys())
    parser.add_argument('--words', choices=['both', 'phrase', 'words'], required=True)
    parser.add_argument('--min_length', type=int, required=True)
    parser.add_argument('--min_score', type=int, default=40)
    args = parser.parse_args()

    # Process arguments.
    alterer = alterers[args.alterer]
    word_style = {'phrase', 'words'} if args.words == 'both' else {args.words}
    min_length = args.min_length
    min_score = args.min_score

    # Perform alterations.
    words = load_words()
    alterations = sorted(
        (
            alteration
            for entry in words
            for alteration in alter_all(alterer, entry, words, word_style, min_length, min_score)
        ),
        # Score descending, length descending, alphabetical
        key=lambda a: (-a[2], -len(''.join(a[1])), a[0]),
    )

    # Print results.
    for phrase, alteration, score in alterations:
        phrase = ' '.join(phrase)
        alteration = (' ' if 'words' in word_style else '').join(alteration)

        print(f"{phrase};{alteration};{score}")

def alter_all(alterer, entry, words, word_style, min_length, min_score, ignore_short=True):
    for phrase in phrases(entry, words, ignore_short):
        if len(phrase) <= 1:
            continue
        if any(p not in words or words[p] < min_score or len(p) < min_length for p in phrase):
            continue

        alteration = alterer(phrase)
        if not alteration:
            continue
        if 'phrase' in word_style and ''.join(alteration) not in words:
            continue
        if 'words' in word_style and any(a not in words or words[a] < min_score for a in alteration):
            continue

        score = min(words[''.join(phrase)], *(words[p] for p in phrase))
        if 'phrase' in word_style:
            score = min(score, words[''.join(alteration)])
        if 'words' in word_style:
            score = min(score, *(words[a] for a in alteration))
        if score < min_score:
            continue

        yield phrase, alteration, score

def semordnilap(phrase):
    if any(p == p[::-1] for p in phrase): return None
    return [p[::-1] for p in reversed(phrase)]

def beheaded(phrase):
    return [p[1:] for p in phrase]

def curtailed(phrase):
    return [p[:-1] for p in phrase]

def inside_out(phrase):
    return [p[0] + p[-1] for p in phrase]

def front_to_back(phrase):
    return [p[1:] + p[0] for p in phrase]

def back_to_front(phrase):
    return [p[-1] + p[:-1] for p in phrase]



if __name__ == '__main__':
    main()

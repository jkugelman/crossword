#!/usr/bin/env python3

from argparse import ArgumentParser
import csv
from itertools import combinations
from sys import stdout, stderr
from textwrap import indent

from lib import grouped_by_len, load_words

def main():
    parser = ArgumentParser()
    parser.add_argument("--pivot_length", type=int, required=True, help="Pivot length")
    parser.add_argument("--min_length", type=int, default=0, help="Minimum length")
    parser.add_argument("--max_length", type=int, default=30, help="Maximum length")
    parser.add_argument("--min_prefix", type=int, default=1, help="Minimum prefix length")
    parser.add_argument("--min_suffix", type=int, default=1, help="Minimum suffix length")
    parser.add_argument("--min_score", type=int, default=10, help="Minimum score")
    args = parser.parse_args()

    words = load_words(min_score=args.min_score)

    csv_writer = csv.writer(stdout)
    show_jumpers(
        csv_writer,
        words,
        pivot_length=args.pivot_length,
        min_length=args.min_length,
        max_length=args.max_length,
        min_prefix=args.min_prefix,
        min_suffix=args.min_suffix,
    )

def jumpers(words, pivot_length, min_length, max_length, min_prefix, min_suffix):
    words_by_len = grouped_by_len(words)

    for length in sorted(words_by_len, reverse=True):
        if length < min_length or length > max_length:
            continue

        for pivot in range(min_prefix - 1, length - (pivot_length - 1) - (min_suffix - 1)):
            print(f"length={length}, pivot={pivot}", file=stderr, flush=True)

            for clued_a, clued_b in combinations(words_by_len[length], 2):
                # Pivot strings must be equal, when reversed.
                if clued_a[pivot:pivot+pivot_length] != clued_b[pivot:pivot+pivot_length][::-1]:
                    continue

                # The two words in the grid must be real words.
                gridded_a = clued_a[:pivot+1] + clued_b[pivot+pivot_length:]
                if gridded_a not in words:
                    continue
                gridded_b = clued_b[:pivot+1] + clued_a[pivot+pivot_length:]
                if gridded_b not in words:
                    continue

                # The beginnings can't be the same.
                if clued_a[:pivot+pivot_length] == clued_b[:pivot+pivot_length]:
                    continue

                # The ends can't be the same.
                if clued_a[pivot:] == clued_b[pivot:]:
                    continue

                # The overall score is the lowest of all four words.
                score = min(words[clued_a], words[clued_b], words[gridded_a], words[gridded_b])

                yield (clued_a, clued_b, pivot, gridded_a, gridded_b, score)

def show_jumpers(csv_writer, words, pivot_length, *args, **kwargs):
    csv_writer.writerow(['clued_a', 'clued_b', 'pivot', 'gridded_a', 'gridded_b', 'score', 'visual'])

    for jumper in jumpers(words, pivot_length, *args, **kwargs):
        clued_a, clued_b, pivot, gridded_a, gridded_b, score = jumper

        # Visualize the find.
        visual = []
        visual.append(f"{gridded_a} ({score})")
        if pivot_length <= 2:
            visual.append(f"{' ' * pivot}|")
        else:
            for i in range(1, pivot_length - 1):
                visual.append(f"{' ' * pivot}{clued_a[pivot + i]}")
        visual.append(f"{gridded_b}")
        visual = "\n".join(visual)

        # Print CSV.
        if csv_writer:
            csv_writer.writerow([clued_a, clued_b, pivot, gridded_a, gridded_b, score, visual])

        # Print nicely to stderr.
        print(f"{indent(visual, '    ')}\n", file=stderr, flush=True)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3

from argparse import ArgumentParser
import csv
from itertools import combinations, product
import re
from sys import stdout, stderr
from textwrap import indent

from lib import grouped_by_len, grouped_by_multi, load_words

def main():
    parser = ArgumentParser()
    parser.add_argument("--pivot_length", type=int_ge(2), required=True, help="Pivot length")
    parser.add_argument("--min_length", type=int, default=0, help="Minimum length")
    parser.add_argument("--max_length", type=int, default=30, help="Maximum length")
    parser.add_argument("--min_prefix", type=int, default=1, help="Minimum prefix length")
    parser.add_argument("--min_suffix", type=int, default=1, help="Minimum suffix length")
    parser.add_argument("--min_score", type=int, default=10, help="Minimum score")
    parser.add_argument("--csv", action="store_true", help="Output as CSV")
    args = parser.parse_args()

    words = load_words(min_score=args.min_score)

    csv_writer = None
    if args.csv:
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
    words_by_pivot = grouped_by_multi(words, keys=lambda word: pivots(word, pivot_length))

    for pivot_a in words_by_pivot:
        pivot_b = pivot_a[::-1]

        if pivot_a > pivot_b:
            continue

        for clued_a, clued_b in product(words_by_pivot[pivot_a], words_by_pivot.get(pivot_b, [])):
            for idx_a, idx_b in product(find_all(clued_a, pivot_a), find_all(clued_b, pivot_b)):
                # Check prefix and suffix lengths.
                if idx_a + 1 < min_prefix:
                    continue
                if idx_b + 1 < min_prefix:
                    continue
                if len(clued_a) - (idx_a + pivot_length) < min_suffix:
                    continue
                if len(clued_b) - (idx_b + pivot_length) < min_suffix:
                    continue

                # The two words in the grid must be real words.
                gridded_a = clued_a[:idx_a+1] + clued_b[idx_b+pivot_length:]
                if gridded_a not in words:
                    continue
                gridded_b = clued_b[:idx_b+1] + clued_a[idx_a+pivot_length:]
                if gridded_b not in words:
                    continue

                if not min_length <= len(gridded_a) <= max_length:
                    continue
                if not min_length <= len(gridded_b) <= max_length:
                    continue

                # The beginnings can't be the same.
                if clued_a[:idx_a+pivot_length] == clued_b[:idx_b+pivot_length]:
                    continue

                # The ends can't be the same.
                if clued_a[idx_a:] == clued_b[idx_b:]:
                    continue

                # No duplicate words.
                if len({clued_a, clued_b, gridded_a, gridded_b}) != 4:
                    continue

                # The overall score is the lowest of all four words.
                low_score = min(words[clued_a], words[clued_b], words[gridded_a], words[gridded_b])
                high_score = max(words[clued_a], words[clued_b], words[gridded_a], words[gridded_b])

                visual = visualize(pivot_length, gridded_a, clued_a, gridded_b, clued_b, idx_a, idx_b)

                yield (
                    visual,
                    low_score, high_score,
                    gridded_a, clued_a,
                    gridded_b, clued_b,
                    idx_a, idx_b,
                    pivot_a, pivot_b,
                )

def pivots(word, pivot_length):
    for i in range(len(word) - pivot_length + 1):
        yield word[i : i + pivot_length]

def find_all(string, substring):
    for match in re.finditer(re.escape(substring), string):
        yield match.start()

def visualize(pivot_length, gridded_a, clued_a, gridded_b, clued_b, idx_a, idx_b):
    visual = []
    visual.append(f"{' ' * max(idx_b - idx_a, 0)}{gridded_a}")
    if pivot_length <= 2:
        visual.append(f"{' ' * max(idx_a, idx_b)}|")
    else:
        for i in range(1, pivot_length - 1):
            visual.append(f"{' ' * max(idx_a, idx_b)}{clued_a[idx_a + i]}")
    visual.append(f"{' ' * max(idx_a - idx_b, 0)}{gridded_b}")
    return "\n".join(visual)

def show_jumpers(csv_writer, words, pivot_length, *args, **kwargs):
    if csv_writer:
        csv_writer.writerow([
            'visual',
            'low_score', 'high_score',
            'gridded_a', 'clued_a',
            'gridded_b', 'clued_b',
            'idx_a', 'idx_b',
            'pivot_a', 'pivot_b',
        ])

    for jumper in jumpers(words, pivot_length, *args, **kwargs):
        visual, low_score, high_score, gridded_a, clued_a, gridded_b, clued_b, idx_a, idx_b, pivot_a, pivot_b = jumper

        # Print it.
        if csv_writer:
            csv_writer.writerow([visual, low_score, high_score, gridded_a, clued_a, gridded_b, clued_b, idx_a, idx_b, pivot_a, pivot_b])
        else:
            print(f"{visual}\n", flush=True)

def int_ge(min_value):
    def checker(value):
        value = int(value)
        if value < min_value:
            raise argparse.ArgumentTypeError(f"{value!r} is too small, must be >= {min_value}")
        return value
    return checker

if __name__ == '__main__':
    main()

#!/usr/bin/env python3

from collections import defaultdict
import concurrent.futures
from itertools import combinations, permutations
import os
import re
import sys

def main():
    if len(sys.argv) < 2:
        eprint(f"Usage: {sys.argv[0]} <wordlist.txt>")
        sys.exit(1)

    # Load the word list.
    with open(sys.argv[1]) as file:
        word_list = load_word_list(file)

    # Autodetect the number of CPU cores.
    max_workers = os.cpu_count()

    # Run multiple `generate_puzzles` call in parallel, up to `max_workers` at a time.
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Generator to provide tasks
        task_generator = find_letter_combinations(word_list)

        # Dictionary to keep track of future to item mapping
        futures = {}

        # Initialize the pool with the first set of tasks
        for _ in range(max_workers):
            try:
                item = next(task_generator)
                future = executor.submit(generate_puzzles, *item)
                futures[future] = item
            except StopIteration:
                break

        # As each task completes, submit a new one
        while futures:
            # Wait for the first future to complete
            done, _ = concurrent.futures.wait(
                futures,
                return_when=concurrent.futures.FIRST_COMPLETED
            )

            for future in done:
                item = futures.pop(future)
                try:
                    result = future.result()
                except Exception as exc:
                    eprint(f'Generated an exception: {exc}')

                # Submit a new task
                try:
                    new_item = next(task_generator)
                    new_future = executor.submit(generate_puzzles, *new_item)
                    futures[new_future] = new_item
                except StopIteration:
                    pass

def load_word_list(file, min_score=0):
    word_list = set()

    for line in file:
        line = line.strip()
        if ';' in line:
            word, score = line.split(';', 1)
            word = re.sub('[^a-z]', '', word.lower())

            score = int(score.split(';')[0])
            if score < min_score:
                continue
        else:
            word = line

        word_list.add(word)

    return word_list

def find_letter_combinations(word_list):
    word_list = {word for word in word_list if len(word) == 3 and len(set(word)) == 3}
    letter_sets = {frozenset(word) for word in word_list}
    already_checked = set()

    for (a, b, c) in combinations(letter_sets, 3):
        letters = a | b | c

        if letters in already_checked:
            continue
        already_checked.add(letters)

        # We need all distinct letters.
        if len(letters) != 9:
            continue

        # Make sure there are enough words to fill a grid.
        words = {word for word in word_list if set(word) <= letters}
        if len(words) < 54:
            continue

        yield (letters, words)

def generate_puzzles(letters, word_list):
    # Are there at least 18 different ways to make a line (row or column) of 3 words?
    lines = combinations(word_list, 3)
    lines = [{a, b, c} for (a, b, c) in lines if len(set(a + b + c)) == 9]
    if not are_enough_line_combinations(lines, 18):
        return

    eprint(''.join(sorted(letters)), flush=True)

    puzzle = [['.' for _ in range(9)] for _ in range(9)]
    match_table = build_match_table(letters, word_list)
    fill_puzzle(puzzle, letters, word_list, match_table, set(), 0)

# Check if there are at least `n` lines with distinct words.
def are_enough_line_combinations(lines, n, used_words=None, start=None):
    if used_words is None: used_words = set()
    if start is None: start = 0

    if n == 0:
        return True

    for i in range(start, len(lines)):
        combo = lines[i]
        if used_words & combo:
            continue
        used_words |= combo
        if are_enough_line_combinations(lines, n - 1, used_words, i + 1):
            return True
        used_words -= combo

    return False

def build_match_table(letters, word_list):
    match_table = dict()

    for length in range(3):
        for prefix in permutations(letters, length):
            prefix = ''.join(prefix)
            pattern = prefix + ('.' * (3 - length))
            matches = {word for word in word_list if word.startswith(prefix)}
            match_table[pattern] = matches

    return match_table

def fill_puzzle(puzzle, letters, word_list, match_table, used_words, n):
    if n >= 27:
        print_puzzle(puzzle)
        return

    row = n % 9
    col = n // 9 * 3

    for word in valid_words_at(puzzle, letters, word_list, match_table, used_words, row, col):
        # The used words includes the across word we're adding,
        # plus the three down words if we finished a 3x3 cell.
        new_words = {word}
        if row % 3 == 2:
            cell_row = row // 3 * 3
            down_words = {''.join(puzzle[cell_row + j][col + i] for j in range(3)) for i in range(3)}
            new_words.update(down_words)
        new_words -= used_words

        puzzle[row][col:col+3] = word
        used_words |= new_words

        fill_puzzle(puzzle, letters, word_list, match_table, used_words, n + 1)

        puzzle[row][col:col+3] = "..."
        used_words -= new_words

def valid_words_at(puzzle, letters, word_list, match_table, used_words, row, col):
    cell_row = row // 3 * 3
    cell_col = col

    row_letters  = {puzzle[row][i] for i in range(9)} - {'.'}
    col_letters  = {puzzle[i][col] for i in range(9)} - {'.'}
    cell_letters = {puzzle[cell_row + i][cell_col + j] for i in range(3) for j in range(3)} - {'.'}

    used_letters = row_letters | col_letters | cell_letters
    unused_letters = letters - used_letters

    available_words = {word for word in (word_list - used_words) if set(word) <= unused_letters}

    for word in available_words:
        puzzle[row][col:col+3] = word
        down_words = {''.join(puzzle[cell_row + j][col + i] for j in range(3)) for i in range(3)}
        puzzle[row][col:col+3] = '...'

        # Are all the down words valid?
        if not all(match_table.get(dw) for dw in down_words):
            continue

        # The down words are filled, so make sure they're unique.
        if row % 3 == 2:
            if len(down_words) != 3:
                continue
            if down_words & used_words:
                continue

        # All checks passed. The word is valid.
        yield word

def print_puzzle(puzzle):
    for row in puzzle:
        print(f"|{' '.join(row)}|", flush=True)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__ == '__main__':
    main()

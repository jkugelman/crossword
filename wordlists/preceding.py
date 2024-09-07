#!/usr/bin/env python3

# Find strings preceding a keyword. If a line contains multiple keywords,
# print each of the prefixes.
#
# For example, searching for `of` in the line `an offer of a lifetime` will
# yield both `an` and `an offer`.

import sys

def grep_preceding_text(search_string):
    for line in sys.stdin:
        line = line.strip()
        start = 0

        while True:
            # Find the search string in the line starting from 'start' index
            index = line.find(search_string, start)
            if index == -1:
                break  # No more occurrences, exit the loop

            # Print the part of the line before the found search string
            print(line[:index])

            # Move the start index to just after the current occurrence
            start = index + len(search_string)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <search_string>")
        sys.exit(1)

    search_string = sys.argv[1]
    grep_preceding_text(search_string)

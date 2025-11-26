#!/usr/bin/env python3

from lib import load_words

def main():
    words = load_words()

    for left, right, width, _height in box(words, min_width=3, min_height=3):
        print(right[:width])
        for i in range(width, len(left) - width):
            print(left[i] + " " * (width - 2) + right[i])
        print(left[-width:])
        print()

def box(words, min_width, min_height):
    def is_palindrome(s):
        return s == s[::-1]

    # Group words by equal length
    groups = {}
    for w in words:
        groups.setdefault(len(w), []).append(w)

    results = set()

    for group in groups.values():
        if len(group) < 2:
            continue

        L = len(group[0])

        # Determine valid widths
        for width in range(min_width, L + 1):
            height = L - 2 * (width - 1)
            if height < min_height:
                continue

            first_map = {}
            last_map = {}

            # Build maps
            for w in group:
                first_seg = w[:width]
                last_seg = w[-width:]

                # Skip words where either overlap segment is palindrome
                if is_palindrome(first_seg) or is_palindrome(last_seg):
                    continue

                first_key = first_seg[::-1]
                last_key = last_seg[::-1]
                first_map.setdefault(first_key, []).append(w)
                last_map.setdefault(last_key, []).append(w)

            # Find matches
            for w in group:
                first_seg = w[:width]
                last_seg = w[-width:]

                # Skip palindromes here too
                if is_palindrome(first_seg) or is_palindrome(last_seg):
                    continue

                possible = set(first_map.get(first_seg, [])) & set(last_map.get(last_seg, []))

                for other in possible:
                    if other != w:
                        pair = tuple(sorted([w, other]))  # ensure uniqueness
                        results.add((pair[0], pair[1], width, height))

    # Sort by width, then height
    results = sorted(results, key=lambda x: (x[2], x[3]))

    return list(results)

if __name__ == '__main__':
    main()

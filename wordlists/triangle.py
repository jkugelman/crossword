#!/usr/bin/env python3
#
# Usage: `./triangle.py A B C < wordlist.txt`
#
# Finds interlocking words of length A, B, and C.

from itertools import groupby
import sys

def main():
    A, B, C = [int(n) for n in sys.argv[1:4]]

    words = sorted((line.strip() for line in sys.stdin), key=len)
    words = {len: list(words) for (len, words) in groupby(words, key=len)}

    first = True

    for a in words[A]:
        for b in words[B]:
            for c in words[C]:
                if len({a, b, c}) != 3:
                    continue

                if a[0] == c[0] and a[-1] == b[0] and b[-1] == c[-1]:
                    if first:
                        print("        *   *        ".rstrip())
                        print("      A B   A C      ".rstrip())
                        print("    A   B   A   C    ".rstrip())
                        print("  A     B   A     C  ".rstrip())
                        print("* C C C *   * B B B *".rstrip())
                        print("                     ".rstrip())
                        print("* A A A *   * C C C *".rstrip())
                        print("  C     B   A     B  ".rstrip())
                        print("    C   B   A   B    ".rstrip())
                        print("      C B   A B      ".rstrip())
                        print("        *   *        ".rstrip())
                        print()
                        first = False

                    print(f"{a} {b} {c}")

if __name__ == '__main__':
    main()

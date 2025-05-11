#!/usr/bin/env python3

# Generates color wheels for Jacob Reed's puzzle.

from argparse import ArgumentParser
from collections import defaultdict

from lib import load_words

def main():
    parser = ArgumentParser()
    parser.add_argument("--min_score", type=int, default=30, help="Minimum score")
    parser.add_argument("--min_length", type=int, default=3, help="Minimum length")
    parser.add_argument("--max_length", type=int, default=6, help="Maximum length")
    args = parser.parse_args()

    words = load_words(min_score=args.min_score)

    colors = {line.strip() for line in open('colors.txt')}
    colors = {
        color for color in colors
        if color in words
            and args.min_length <= len(color) <= args.max_length
    }

    for direction in ['clockwise', 'counterclockwise']:
        for wheel in color_wheels(colors, words, direction):
            score = min(words[word] for word in wheel + rotated(wheel, direction))
            print(f"{direction} {score}: {', '.join(wheel)} -> {', '.join(rotated(wheel, direction))}", flush=True)

def color_wheels(colors, words, direction):
    """
    Yield every 8-tuple `wheel` of colors satisfying:

      1. Opposite slots have equal length.
      2. Rotating the first letters (0–3) and last letters (4–7)
         one slot in the given `direction` yields 8 new words that
         each differ in the replaced letter and exist in `words`.

    `direction` must be "counterclockwise" or "clockwise".
    """
    words_set = set(words)

    # bucket colors by length for the opposite-slot constraint
    by_len = defaultdict(list)
    for c in colors:
        by_len[len(c)].append(c)

    # decide fill order: 0→1→…→7 for CCW, 7→6→…→0 for CW
    if direction == "counterclockwise":
        order = list(range(8))
    else:
        order = list(reversed(range(8)))

    wheel = [None] * 8
    used = set()

    def check_full():
        # collect the “source” letters
        letters = [w[0] for w in wheel[:4]] + [w[-1] for w in wheel[4:]]
        if direction == "counterclockwise":
            rotated = letters[-1:] + letters[:-1]
        else:
            rotated = letters[1:] + letters[:1]

        # validate each replacement both changes a letter and is in words_set
        for i, w in enumerate(wheel):
            if i < 4:
                new_word = rotated[i] + w[1:]
                if rotated[i] == w[0] or new_word not in words_set:
                    return False
            else:
                new_word = w[:-1] + rotated[i]
                if rotated[i] == w[-1] or new_word not in words_set:
                    return False
        return True

    def backtrack(pos):
        # once we’ve assigned all slots, do the full check
        if pos == len(order):
            if check_full():
                yield tuple(wheel)
            return

        slot = order[pos]
        opp = (slot + 4) % 8

        # enforce opposite-slot same-length if that slot is already placed
        if opp in order[:pos]:
            candidates = by_len[len(wheel[opp])]
        else:
            candidates = colors

        for c in candidates:
            if c in used:
                continue

            wheel[slot] = c
            used.add(c)

            # early prune: for any pos>0, the source slot is order[pos-1]
            if pos > 0:
                src = order[pos - 1]
                # get its first‐or‐last letter
                rot = wheel[src][0] if src < 4 else wheel[src][-1]

                # build and test the one rotated word for this slot
                if slot < 4:
                    if rot == c[0] or (rot + c[1:]) not in words_set:
                        used.remove(c)
                        continue
                else:
                    if rot == c[-1] or (c[:-1] + rot) not in words_set:
                        used.remove(c)
                        continue

            # recurse into the next position
            yield from backtrack(pos + 1)
            used.remove(c)

    yield from backtrack(0)

def rotated(wheel, direction):
    """
    Given a tuple of 8 color‐name strings `wheel`, returns a tuple of the 8 "rotated" words.
    """
    if direction == 'counterclockwise':
        return (
            wheel[7][-1] + wheel[0][1:],
            wheel[0][0] + wheel[1][1:],
            wheel[1][0] + wheel[2][1:],
            wheel[2][0] + wheel[3][1:],
            wheel[4][:-1] + wheel[3][0],
            wheel[5][:-1] + wheel[4][-1],
            wheel[6][:-1] + wheel[5][-1],
            wheel[7][:-1] + wheel[6][-1],
        )
    else:
        return (
            wheel[1][0] + wheel[0][1:],
            wheel[2][0] + wheel[1][1:],
            wheel[3][0] + wheel[2][1:],
            wheel[4][-1] + wheel[3][1:],
            wheel[4][:-1] + wheel[5][-1],
            wheel[5][:-1] + wheel[6][-1],
            wheel[6][:-1] + wheel[7][-1],
            wheel[7][:-1] + wheel[0][0],
        )

if __name__ == '__main__':
    main()

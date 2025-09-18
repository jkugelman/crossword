#!/usr/bin/env python3

# Find words that can be split in two directions at the end, forming another entry.
#
#         ^
#         |
#         |
# --------+
#         |
#         |
#         V

from collections import defaultdict
from lib import load_words

def main():
    words = load_words(min_score=40)

    heads_by_tail = defaultdict(set)
    for word in words:
        for i in range(1, len(word)):
            head = word[:i]
            tail = word[i:]
            heads_by_tail[tail].add(head)

    for word in words:
        for i in range(1, len(word) - 1):
            top = word[:i+1][::-1]
            bottom = word[i:]
            if top == bottom:
                continue
            if top == bottom + 's' or bottom == top + 's':
                continue
            if len(top) == 2 and top.endswith('s'):
                continue
            if len(bottom) == 2 and bottom.endswith('s'):
                continue

            top_heads = heads_by_tail[top]
            bottom_heads = heads_by_tail[bottom]
            shared_heads = top_heads & bottom_heads

            down = top[::-1] + bottom[1:]
            for shared_head in shared_heads:
                across = shared_head + bottom[0]
                if across not in words:
                    continue
                if len(across) < 5:
                    continue
                if len(down) < 5:
                    continue

                for c in top[1:][::-1]:
                    print(f"{' ' * len(shared_head)}{c}")
                print(f"{shared_head}{bottom[0]}")
                for c in bottom[1:]:
                    print(f"{' ' * len(shared_head)}{c}")
                print(flush=True)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3

import copy
import string

def load_word_scores():
    lines = (line.strip() for line in open('XwiJeffChenList.txt'))
    entries = (line.split(';') for line in lines)
    return {word.upper(): int(score) for word, score in entries}

scores = load_word_scores()
words = scores.keys()

long_words = {word for word in words if len(word) == 21}

L = []

for i in range(21):
    L.append(dict())

    for letter in string.ascii_uppercase:
        L[i][letter] = set()

    for word in long_words:
        L[i][word[i]].add(word)

    L[i][' '] = long_words

grid = [[' ' for i in range(21)] for j in range(21)]

for t0 in long_words:
    for r0 in L[0][t0[-1]]:
        for b0 in L[-1][r0[-1]]:
            for l0 in L[-1][b0[0]] & L[0][t0[0]]:
                for t1 in L[0][l0[1]] & L[-1][r0[1]]:
                    for r1 in L[0][t0[-2]] & L[1][t1[-2]] & L[-1][b0[-2]]:
                        for b1 in L[0][l0[-2]] & L[-2][r1[-2]] & L[-1][r0[-2]]:
                            for l1 in L[0][t0[1]] & L[1][t1[1]] & L[-2][b1[1]] & L[-1][b0[1]]:
                                sides = [t0, r0, b0, l0, t1, r1, b1, l1]
                                if len(set(sides)) != len(sides):
                                    continue

                                print(t0)
                                print(t1)
                                for i in range(2, 19):
                                    print(f"{l0[i]}{l1[i]}                 {r1[i]}{r0[i]}")
                                print(b1)
                                print(b0)
                                print()

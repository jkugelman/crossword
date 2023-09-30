#!/usr/bin/env python3

import fileinput

for line in fileinput.input():
    parts = line.strip().split(';', 3)
    word = parts[0]
    score = int(parts[1])
    clue = None
    if len(parts) >= 3:
        clue = parts[2]

    if score == 1:
        score = 1
    elif 2 <= score <= 5:
        score = 5
    elif 6 <= score <= 30:
        score = 25
    elif 31 <= score <= 40:
        score = 30
    elif score == 41:
        score = 31
    elif 42 <= score <= 45:
        score = 40
    elif score == 46:
        score = 41
    elif 47 <= score <= 50:
        score = 50
    elif score == 51:
        score = 51
    elif 52 <= score <= 60:
        score = 60
    elif score == 61:
        score = 61
    else:
        raise Exception(line)

    if clue:
        print(f'{word};{score};{clue}')
    else:
        print(f'{word};{score}')

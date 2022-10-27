#!/usr/bin/env python3

def load_word_scores():
    lines = (line.strip() for line in open('XwiJeffChenList.txt'))
    entries = (line.split(';') for line in lines)
    return {word.upper(): int(score) for word, score in entries}

scores = load_word_scores()
words = scores.keys()

alternates = {}

for word in sorted(words, key=len, reverse=True):
    odd = word[0::2]
    even = word[1::2]

    if odd in words and even in words:
        alternates[word] = 10*len(word) + scores[word] + scores[odd] + scores[even]

for word in sorted(alternates.keys(), key=lambda w: alternates[w], reverse=True):
    odd = word[0::2]
    even = word[1::2]

    print(f"{word} ({scores[word]}) = {odd} ({scores[odd]}) + {even} ({scores[even]})")

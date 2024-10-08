#!/usr/bin/env python3

import os
import re

class WordList:
    def __init__(self):
        self.words = {}

    def load(
        self,
        path,
        edits=[],
    ):
        with open(rel_path(path)) as file:
            words = dict()

            for line in file:
                word, score = line.split(';', 1)
                word = re.sub('[^a-z]', '', word.lower())
                score = int(score.split(';')[0])

                for edit in edits:
                    old = (word, score)
                    word, score = edit(word, score)

                    if score < 0:
                        break

                if score < 0:
                    continue

                words[word] = score

            for word, score in words.items():
                self.words.setdefault(word, score)

    def save(self, path, scores, min_score=0):
        with open(rel_path(path), 'w') as file:
            for (word, score) in sorted(self.words.items()):
                if score >= min_score:
                    file.write(f'{word};{score}\n' if scores else f'{word}\n')

def filter(min_score=None, max_score=None, min_length=None, max_length=None):
    def filter(word, score):
        if min_score != None and score < min_score:
            return (word, -1)
        if max_score != None and score > max_score:
            return (word, -1)
        if min_length != None and len(word) < min_length:
            return (word, -1)
        if max_length != None and len(word) > max_length:
            return (word, -1)
        return (word, score)
    return filter

def xwi_renumber(word, score):
    if score >= 60:
        return (word, 60)
    if score >= 50:
        return (word, 50)
    if score >= 30:
        return (word, 30)
    elif score >= 25:
        return (word, 20)
    else:
        return (word, 20)

def rel_path(path):
    return os.path.join(os.path.dirname(__file__), path)

def load_word_list(min_score=0):
    word_list = WordList()

    word_list.load('jkugelman-wordlist.txt')
    word_list.load('XwiJeffChenList.txt', [xwi_renumber])
    word_list.load('spreadthewordlist.txt', [filter(min_score=50)])
    word_list.words = {word: score for (word, score) in word_list.words.items() if score >= min_score}

    bonuses = load_bonuses('jkugelman-clues.txt')
    for word, bonus in bonuses.items():
        try:
            word_list.words[word] += bonus
        except KeyError:
            pass

    return word_list

def load_bonuses(path):
    bonuses = {}

    with open(rel_path(path)) as file:
        for line in file:
            word_with_stars = line.strip().split(';')[0]
            word = word_with_stars.lstrip('*')
            star_count = len(word_with_stars) - len(word)
            score = 1 + star_count
            if score > bonuses.get(word, 0):
                bonuses[word] = score

    return bonuses

def save_word_list(word_list):
    word_list.save('wordlist.txt', scores=True)
    word_list.save('unscored.txt', scores=False, min_score=20)

if __name__ == '__main__':
    word_list = load_word_list()
    save_word_list(word_list)

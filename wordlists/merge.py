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
        with open(path) as file:
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

                self.words.setdefault(word, score)

    def save(self, path):
        with open(path, 'w') as file:
            for (word, score) in sorted(self.words.items()):
                file.write(f'{word};{score}\n')

def filter_score(min=None, max=None):
    def filter(word, score):
        if min != None and score < min:
            return (word, -1)
        if max != None and score > max:
            return (word, -1)
        return (word, score)
    return filter

def xwi_renumber(word, score):
    if score >= 60:
        return (word, 60)
    if score >= 50:
        return (word, 50)
    if score >= 30:
        return (word, 40)
    elif score >= 25:
        return (word, 30)
    elif score >= 20:
        return (word, 20)
    elif score >= 10:
        return (word, 10)
    else:
        return (word, 0)

script_dir = os.path.dirname(__file__)

word_list = WordList()
word_list.load(os.path.join(script_dir + '/personal.txt'))
word_list.load(os.path.join(script_dir + '/XwiJeffChenList.txt'), [filter_score(min=51), xwi_renumber])
word_list.load(os.path.join(script_dir + '/XwiJeffChenList.txt'), [filter_score(max=50), xwi_renumber])
word_list.load(os.path.join(script_dir + '/spreadthewordlist.txt'))
word_list.save(os.path.join(script_dir + '/merged.txt'))

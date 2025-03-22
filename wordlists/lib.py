#!/usr/bin/env python3

import os
import re

def load_words(min_score=0):
    """
    Loads the words from STWL + XWI + jkugelman-wordlist.txt.
    """

    words = {}

    _load(words, 'jkugelman-wordlist.txt')
    _load(words, 'XwiJeffChenList.txt', [_xwi_renumber])
    _load(words, 'spreadthewordlist.txt', [_filter(min_score=50)])

    return {word: score for (word, score) in words.items() if score >= min_score}

def _load(words, path, edits=[]):
    with open(_rel_path(path)) as file:
        new_words = dict()

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

            new_words[word] = score

        for word, score in new_words.items():
            words.setdefault(word, score)

def _filter(min_score=None, max_score=None, min_length=None, max_length=None):
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

def _xwi_renumber(word, score):
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

def _rel_path(path):
    return os.path.join(os.path.dirname(__file__), path)

def phrases(entry, words, ignore_short=True):
    """
    Figures out if `entry` can be made from any combination of words in `words`. All valid
    splittings are yielded.

    If `ignore_short` is true (the default), 1- and 2-letter words with score < 50 are ignored.
    This way "a" and "I" and "of/we/it" can be used, but not abbreviations like "ep" and "rd".
    """

    # Filter out 1- and 2-letter words under 50.
    if isinstance(words, dict) and ignore_short:
        words = {word: score for word, score in words.items() if len(word) >= 3 or score >= 50}

    for i in range(1, len(entry)):
        prefix, suffix = entry[:i], entry[i:]
        if prefix in words:
            for phrase in phrases(suffix, words):
                yield [prefix] + phrase
    if entry in words:
        yield [entry]

def synonyms(word):
    """
    Retrieves synonyms for a word using NLTK WordNet.

    To use:

    ```
    $ docker run -it --rm -v $PWD:/home -w /home python bash
    # pip install nltk
    # python
    >>> import nltk
    >>> nltk.download('wordnet')
    ```
    """

    from nltk.corpus import wordnet as wn

    synonyms = set()
    for synset in wn.synsets(word):
        for lemma in synset.lemmas():
            synonyms.add(lemma.name().replace('_', '').lower())

    # Remove the word and its singular/plural.
    synonyms.discard(word)
    synonyms.discard(word + 's')
    if word.endswith('s'):
        synonyms.discard(word[:-1])

    return synonyms

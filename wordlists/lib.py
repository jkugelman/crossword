#!/usr/bin/env python3

from collections import defaultdict
import os
import re

def load_words(min_score=0, bonuses=False):
    """
    Loads STWL + XWI + `jkugelman-wordlist.txt`. If `bonuses` is `True`, also gives extra points to
    entries from `jkugelman-clues.txt`.
    """

    words = {}

    _load(words, 'jkugelman-wordlist.txt')
    _load(words, 'XwiJeffChenList.txt', _xwi_renumber)
    _load(words, 'spreadthewordlist.txt', _stwl_renumber)
    _load(words, 'peter-broda-wordlist__gridtext__scored__july-25-2023.txt', _broda_renumber)

    if bonuses:
        _add_bonuses(words, 'jkugelman-clues.txt')

    return {word: score for (word, score) in words.items() if score >= min_score}

def save_words(words, path, scores=True, min_score=10):
    """
    Saves the wordlist `words` to a text file at `path`. If `scores` is `False` the scores are
    omitted. Words below `min_score` are filtered out.
    """
    with open(rel_path(path), 'w') as file:
        for (word, score) in sorted(words.items()):
            if score >= min_score:
                file.write(f'{word};{score}\n' if scores else f'{word}\n')

def _load(words, path, filter=None):
    with open(rel_path(path)) as file:
        new_words = dict()

        for line in file:
            word, score = line.split(';', 1)
            word = re.sub('[^a-z]', '', word.lower())
            score = int(score.split(';')[0])

            if filter:
                score = filter(word, score)

            if score is not None:
                new_words[word] = score

        for word, score in new_words.items():
            words.setdefault(word, score)

def _xwi_renumber(word, score):
    if score >= 60:
        return 60
    if score >= 50:
        return 50
    if score >= 30:
        return 30
    elif score >= 25:
        return 20
    else:
        return 20

def _stwl_renumber(word, score):
    if score >= 50:
        return 50
    else:
        return None

def _broda_renumber(word, score):
    # Based on what Sid Sivakumar says in
    # https://www.youtube.com/live/pfC5EZVki7A?si=w7f8sgVCdwlNEZbN&t=975
    if len(word) < 7:
        return None
    if score >= 80:
        return 60
    else:
        return None

def _add_bonuses(words, path):
    bonuses = {}
    with open(rel_path(path)) as file:
        for line in file:
            word_with_stars = line.strip().split(';')[0]
            word = word_with_stars.lstrip('*')
            star_count = len(word_with_stars) - len(word)
            score = 1 + star_count
            if score > bonuses.get(word, 0):
                bonuses[word] = score

    for word, bonus in bonuses.items():
        try:
            words[word] += bonus
        except KeyError:
            pass

def grouped_by(items, key):
    """
    Returns a dictionary where the `items` are grouped by `key(item)`.
    """
    grouped = defaultdict(set)
    for item in items:
        grouped[key(item)].add(item)
    return grouped

def grouped_by_len(items):
    """
    Returns a dictionary where the `items` are grouped by `len`.
    """
    return grouped_by(items, key=len)

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
    Retrieves synonyms for a word using NLTK WordNet and Roget's Thesaurus.

    To use:

    ```
    $ docker run -it --rm -v $PWD:/home -w /home python bash
    # pip install nltk lxml
    # python
    >>> import nltk
    >>> nltk.download('wordnet')
    ```
    """
    return synonyms_nltk(word) | synonyms_roget(word)

def synonyms_nltk(word):
    from nltk.corpus import wordnet as wn

    return _normalize(
        word,
        (
            lemma.name()
            for synset in wn.synsets(word)
            for lemma in synset.lemmas()
        ),
    )

def synonyms_roget(word):
    import roget

    return _normalize(
        word,
        (
            entry
            for pos in roget.parts_of_speech
            for entries in roget.all_entries(word, pos)
            for entry in entries
        ),
    )

def _normalize(word, synonyms):
    synonyms = {re.sub('[^a-z]', '', synonym.lower()) for synonym in synonyms}
    synonyms -= {''}

    synonyms.discard(word)
    synonyms.discard(word + 's')
    if word.endswith('s'):
        synonyms.discard(word[:-1])

    return synonyms

def spell_meta(meta, themers, min_count=None, max_count=None):
    """
    Yields sets of themers that spell the meta answer.

    * `meta` is the meta answer.
    * `themers` maps theme entries to the letter or string they contribute to the meta answer.
    * `min_count` and `max_count` limit how many themers can be used.

    Example:

    spell_meta(
        'fries',
        {'foodless': 'f',
         'romania': 'r',
         'ifatall': 'i',
         'emerita': 'e',
         'stormed': 's'},
    )
    """
    return spell_metas(
        [meta],
        {themer: [contribution] for themer, contribution in themers.items()},
        min_count,
        max_count,
    )

def spell_metas(metas, themers, min_count=None, max_count=None):
    """
    Yields sets of themers that spell all the meta answers.

    * `themers` maps theme entries to the letters or strings they contribute to the meta answers.
    * `metas` is an iterable of meta answers.
    * `min_count` and `max_count` limit how many themers can be used.

    Example:

    spell_meta(
        ['fries', 'salad'],
        {'foodless': ['f', 's'],
         'romania': ['r', 'a'],
         'ifatall': ['i', 'l'],
         'emerita': ['e', 'a'],
         'stormed': ['s', 'd']},
    )
    """
    print(f"spell_metas: {metas}?")
    def spell_metas_r(metas, used_themers):
        if all(not meta for meta in metas):
            if min_count is None or len(used_themers) >= min_count:
                yield used_themers
            return

        if max_count is not None and len(used_themers) >= max_count:
            return

        for themer, contributions in themers.items():
            if themer in used_themers:
                continue

            new_metas = []
            for contribution, meta in zip(contributions, metas):
                if not meta.startswith(contribution):
                    break
                new_metas.append(meta[len(contribution):])
            else:
                yield from spell_metas_r(new_metas, used_themers + [themer])

    yield from spell_metas_r(metas, [])

def is_symmetrical(themers):
    """
    Checks if a list of theme entries has symmetrical lengths.
    """
    lengths = [len(themer) for themer in themers]
    return lengths == lengths[::-1]

def spellable_metas(themers, words, min_count=None, max_count=None, filter=is_symmetrical):
    """
    Finds meta answers that can be spelled from a set of potential theme entries. Yields these
    answers and the theme sets that can spell them.

    * `themers` maps theme entries to the letter or string they contribute to the meta answer.
    * `words` is the word list to search through.
    * `min_count` and `max_count` limit how many themers can be used.
    * `filter` is a function that returns `True` for acceptable theme sets. The default only accepts
      symmetrical theme sets.
    """
    for word in words:
        spellings = [spelling for spelling in spell_meta(word, themers) if filter(spelling)]
        if spellings:
            yield word, spellings

def is_palindrome(word):
    return word == word[::-1]

def rel_path(path):
    return os.path.join(os.path.dirname(__file__), path)

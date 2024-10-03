#!/usr/bin/env python3

from collections import defaultdict
import csv
import re

def main():
    movie_titles = load_movies(min_votes=10000)

    double_features = find_overlapping_titles(movie_titles)
    for _, double_feature in double_features:
        if len(double_feature) > 27:
            continue
        print(double_feature)

def load_movies(min_votes):
    movies = {}

    with open('imdb-title.basics.tsv') as basics:
        reader = csv.reader(basics, delimiter='\t', quoting=csv.QUOTE_NONE)
        for row in reader:
            (tconst, title_type, primary_title, original_title, is_adult, start_year, end_year, runtime_minutes, genres) = row
            if title_type != 'movie':
                continue
            movies[tconst] = {'title': primary_title, 'average_rating': None, 'num_votes': None}

    with open('imdb-title.ratings.tsv') as ratings:
        reader = csv.reader(ratings, delimiter='\t', quoting=csv.QUOTE_NONE)
        for row in reader:
            (tconst, average_rating, num_votes) = row
            if tconst not in movies:
                continue
            movies[tconst]['average_rating'] = float(average_rating)
            movies[tconst]['num_votes'] = int(num_votes)

    movies = {movie['title']: movie['average_rating'] for movie in movies.values() if (movie['num_votes'] or 0) >= min_votes}
    movies = list(sorted(movies.keys(), key=lambda title: movies[title], reverse=True))

    return movies

def clean_title(title):
    # Remove punctuation, convert to lowercase, replace hyphens with spaces
    title_clean = re.sub(r'[^\w\s-]', '', title.lower())
    title_clean = title_clean.replace('-', ' ')
    words = title_clean.split()
    return title_clean, words

def generate_possible_endings(words, clean_title):
    possible_endings_words = []
    possible_endings_letters = []
    n = len(words)
    # Generate word endings
    for i in range(n-1, -1, -1):
        ending_words = words[i:]
        # Exclude full title
        if i == 0:
            continue
        possible_endings_words.append(' '.join(ending_words))
    # Generate letter endings of length >=4
    for i in range(len(clean_title)-4, 0, -1):
        ending_letters = clean_title[i:]
        # Exclude full title
        if i == 0:
            continue
        if len(ending_letters) >= 4:
            possible_endings_letters.append(ending_letters)
    return possible_endings_words + possible_endings_letters

def generate_possible_starts(words, clean_title):
    #articles = {'a', 'an', 'the'}
    articles = set()
    possible_starts_words = []
    possible_starts_letters = []
    n = len(words)
    start_indices = [0]
    # If the first word is an article, consider starting from the next word
    if words and words[0] in articles:
        start_indices.append(1)
    # Generate word starts
    for idx in start_indices:
        for i in range(idx+1, n+1):
            start_words = words[idx:i]
            # Exclude full title
            if idx == 0 and i == n:
                continue
            possible_starts_words.append(' '.join(start_words))
    # Generate letter starts of length >=4
    for i in range(4, len(clean_title)+1):
        start_letters = clean_title[:i]
        # Exclude full title
        if i == len(clean_title):
            continue
        possible_starts_letters.append(start_letters)
    return possible_starts_words + possible_starts_letters

def find_overlapping_titles(movie_titles):
    articles = {'a', 'an', 'the'}
    # Store movies with their processed data
    movies = []
    for idx, title in enumerate(movie_titles):
        clean, words = clean_title(title)
        possible_endings = generate_possible_endings(words, clean)
        possible_starts = generate_possible_starts(words, clean)
        movies.append({
            'original_title': title,
            'clean_title': clean,
            'words': words,
            'possible_endings': possible_endings,
            'possible_starts': possible_starts,
            'index': idx  # Position in the list (rating)
        })

    # Build EndingsDict
    endings_dict = defaultdict(list)
    for movie in movies:
        for ending in movie['possible_endings']:
            endings_dict[ending].append(movie)

    # Find matching titles
    matches = []
    for movie in movies:
        for start in movie['possible_starts']:
            if start not in endings_dict:
                continue

            for end_movie in endings_dict[start]:
                # Avoid matching a title with itself
                if movie['original_title'] == end_movie['original_title']:
                    continue
                # Ensure overlapping substring is acceptable
                overlap_len = len(start.replace(' ', ''))
                is_full_word = start in movie['words'] and start in end_movie['words']
                if not (is_full_word or overlap_len >= 4):
                    continue

                # Ensure titles are not completely contained within each other
                if start == movie['clean_title'] or start == end_movie['clean_title']:
                    continue

                # Build the concatenated title
                concatenated_title = end_movie['original_title'] + movie['original_title'][len(start):]
                # Scoring heuristic (sum of indices, lower is better)
                score = end_movie['index'] + movie['index']
                matches.append((score, concatenated_title))

    # Deduplicate matches
    matches = list(set(matches))

    # Sort matches by score
    matches.sort(key=lambda x: x[0])

    return matches

if __name__ == '__main__':
    main()

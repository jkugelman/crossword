#!/usr/bin/env python3

import csv
import re
import sys

def title_len(movie):
    return len(re.sub(r'\W', '', movie[5]))

def ranking(movie):
    return float(movie[8]) if movie[8] else 0.0

length = int(sys.argv[1]) if len(sys.argv) >= 2 else None
movies = csv.reader(open("movies.csv"))

next(movies)

movies = (movie for movie in movies if length is None or title_len(movie) == length)

for movie in sorted(movies, key=ranking, reverse=True):
    print("{:<40} {} ({})".format(movie[5], movie[14] or "???", movie[8] or "?"))

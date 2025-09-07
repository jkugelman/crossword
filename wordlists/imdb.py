#!/usr/bin/env python3

# Merge `imdb-title.basics.tsv` with `imdb-title.ratings.tsv`.

import csv
import re
import sys
import unicodedata

def main():
    # Output fieldnames = basics fields + ratings fields
    fieldnames = [
        "tconst",
        "titleType", "primaryTitle", "originalTitle",
        "isAdult",
        "startYear", "endYear",
        "runtimeMinutes",
        "genres",
        "averageRating", "numVotes",
    ]
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for row in movies():
        writer.writerow(row)

def movies():
    # Load ratings into a dict: tconst -> (averageRating, numVotes)
    ratings = {}
    with open('imdb-title.ratings.tsv') as ratings_file:
        ratings_reader = csv.DictReader(ratings_file, delimiter="\t")
        for row in ratings_reader:
            tconst = row["tconst"]
            ratings[tconst] = (row["averageRating"], row["numVotes"])

    with open('imdb-title.basics.tsv') as basics_file:
        basics_reader = csv.DictReader(basics_file, delimiter="\t")
        for row in basics_reader:
            tconst = row["tconst"]
            if tconst in ratings:
                avg, votes = ratings[tconst]
                row["averageRating"] = avg
                row["numVotes"] = votes
            else:
                # IMDb null token is "\N"
                row["averageRating"] = r"\N"
                row["numVotes"] = r"\N"
            row["title"] = clean(row["primaryTitle"])
            yield row

def clean(s: str) -> str:
    # Normalize Unicode (decompose accents into separate marks)
    nfkd_form = unicodedata.normalize('NFKD', s)
    # Encode to ASCII bytes, ignoring characters that can't be converted
    ascii_str = nfkd_form.encode('ASCII', 'ignore').decode('utf-8')
    # Keep only alphanumeric characters, convert to lowercase
    return re.sub(r'[^A-Za-z0-9]', '', ascii_str.lower())

if __name__ == "__main__":
    main()

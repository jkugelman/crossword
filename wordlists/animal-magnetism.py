#!/usr/bin/env python3

# Your list of pairs
pairs = [
    # (0, (("ape", "POLICE TAPE"), ("elk", "LEG SHACKLE"))),
    # (0, (("ray", "CHEESE TRAY"), ("elk", "DILL PICKLE"))),
    # (0, (("ray", "HARRY CARAY"), ("rat", "MLB ALLSTAR"))),
    # (0, (("ray", "OCEAN SPRAY"), ("dog", "WRATH OF GOD"))),
    # (0, (("ray", "VEGGIE TRAY"), ("elk", "DILL PICKLE"))),
    # (1, (("ant", "CONGREGANT"), ("dog", "FINDING GOD"))),
    # (1, (("ant", "INTOXICANT"), ("bat", "RUNNING TAB"))),
    # (1, (("ant", "POWER PLANT"), ("rat", "ENERGYSTAR"))),
    # (1, (("ant", "PROTESTANT"), ("dog", "FINDING GOD"))),
    # (1, (("ape", "BOOK ON TAPE"), ("emu", "NOM DE PLUME"))),
    # (1, (("ass", "DRAMA CLASS"), ("rat", "FALLEN STAR"))),
    # (1, (("ass", "SCREEN PASS"), ("elk", "NOSE TACKLE"))),
    # (1, (("gar", "SAMMY HAGAR"), ("rat", "LEAD GUITAR"))),
    # (1, (("ram", "FINSTAGRAM"), ("gar", "HUMBLE BRAG"))),
    # (2, (("ant", "ACCOUNTANT"), ("bat", "RUNNING TAB"))),
    # (2, (("ant", "RESTAURANT"), ("bat", "RUNNING TAB"))),
    # (2, (("ass", "NIGHT CLASS"), ("ram", "BAD GRAMMAR"))),
    (2, (("ape", "FIRE ESCAPE"), ("gnu", "LADDER RUNG"))),
    (2, (("ass", "GREEN GRASS"), ("elk", "PERIWINKLE"))),
    (3, (("ass", "MUSCLE MASS"), ("elk", "NOSE TACKLE"))),
    (3, (("eel", "COLOR WHEEL"), ("elk", "PERIWINKLE"))),
    (3, (("eel", "SIZZLE REEL"), ("rat", "RISING STAR"))),
    # (4, (("ass", "MUSCLE MASS"), ("rat", "ACTION STAR"))),
    # (4, (("ass", "NO LOOK PASS"), ("rat", "NBA ALL STAR"))),
    (4, (("ass", "NO LOOK PASS"), ("rat", "SOCCER STAR"))),
    (4, (("ass", "SPIRAL PASS"), ("gnu", "STEVE YOUNG"))),
    # (4, (("eel", "ABS OF STEEL"), ("rat", "ACTION STAR"))),
    (4, (("eel", "MAN OF STEEL"), ("rat", "ACTION STAR"))),
    (4, (("owl", "NOODLE BOWL"), ("gnu", "EGG FOO YUNG"))),
    (5, (("ant", "CONGREGANT"), ("dog", "HOUSE OF GOD"))),
    (5, (("ant", "KOBE BRYANT"), ("rat", "NBA ALL STAR"))),
    # (5, (("ass", "BIBLE CLASS"), ("dog", "HOUSE OF GOD"))),
    (5, (("ass", "SUNDAY MASS"), ("dog", "HOUSE OF GOD"))),
]

# Function to find all valid sets of four pairs with eight unique animal names
def find_valid_sets(pairs):
    from itertools import combinations

    # Function to get all animal names in a set of pairs
    def get_animal_names(pair_set):
        animal_names = set()
        for pair in pair_set:
            for inner_pair in pair[1]:
                animal_names.add(inner_pair[0])
        return animal_names

    # List of all valid sets
    valid_sets = []

    # Loop over all combinations of four pairs
    for combo in combinations(pairs, 4):
        animal_names = get_animal_names(combo)

        # Check if the combination has 8 unique animal names
        if len(animal_names) == 8:
            # Calculate the total score for the set
            total_score = (min(x[0] for x in combo), sum(x[0]**2 for x in combo))
            valid_sets.append((total_score, combo))

    # Sort valid sets by their total score in descending order
    valid_sets.sort(reverse=True, key=lambda x: x[0])

    return valid_sets


# Get all valid sets
valid_sets = find_valid_sets(pairs)

# Print the sets with their scores
for idx, valid_set in enumerate(valid_sets):
    score, set_pairs = valid_set
    print(f"Set {idx + 1}: Total score = {score}")
    for (score, pair) in set_pairs:
        print(f"  ({score}, {pair})")
    print("\n")


#!/usr/bin/env python3

import pronouncing
import sys

arg = sys.argv[1]

if phones := pronouncing.phones_for_word(arg):
    print(phones)
elif words := pronouncing.search(arg):
    print(words)

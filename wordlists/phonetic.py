#!/usr/bin/env python3

import pronouncing
import sys

for arg in sys.argv[1:]:
    if phones := pronouncing.phones_for_word(arg):
        print(f"{arg}: {phones}", flush=True)
    elif words := pronouncing.search(arg):
        print(f"{arg}: {words}", flush=True)
    else:
        print(f"{arg}: -", flush=True)

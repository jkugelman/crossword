#!/usr/bin/env python3

import fileinput
import re

for phrase in fileinput.input():
    phrase = phrase.strip()
    if (phrase.count('c') == phrase.count('t') > 0 and
        re.match('^[^c]+[^t]+$', phrase)):
        covert = phrase.replace('c', 'T').replace('t', 'c').replace('T', 't')
        print(f"{phrase} -> {covert}")

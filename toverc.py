#!/usr/bin/env python3

import fileinput
import re

bads = {
    'tcion',
    'dapcer',
    'tacion',
    'tacing',
    'tarcer',
    'cuac',
    'attepc',
    'wretk',
    'retord',
}

for phrase in fileinput.input():
    phrase = phrase.strip()
    if (phrase.count('c') == phrase.count('t') > 0 and
        re.match('^[^t]+[^c]+$', phrase)):
        covert = phrase.replace('c', 'T').replace('t', 'c').replace('T', 't')
        if any(bad in covert for bad in bads):
            continue
        print(f"{phrase} -> {covert}")

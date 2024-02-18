#!/usr/bin/env python3

import sys

def main():
    mappings = {
        'across': {
            'A': 'A',
            'H': 'H',
            'I': 'I',
            'J': 'L',
            'L': 'J',
            'M': 'M',
            'O': 'O',
            'S': 'Z',
            'T': 'T',
            'U': 'U',
            'V': 'V',
            'W': 'W',
            'X': 'X',
            'Y': 'Y',
            'Z': 'S',
        },

        'down': {
            'B': 'B',
            'C': 'C',
            'D': 'D',
            'E': 'E',
            'H': 'H',
            'I': 'I',
            'K': 'K',
            'M': 'W',
            'O': 'O',
            'P': 'B',  # P -> b?
            'S': 'Z',
            'U': 'N',  # U -> n?
            'W': 'M',
            'X': 'X',
            'Z': 'S',
        },
    }

    if len(sys.argv) != 4:
        eprint(f"Usage: {sys.argv[0]} <{'|'.join(mappings.keys())}> <score> <wordlist.txt>")
        eprint()
        eprint(f"Output: <word>;<score>;<full word> (<num letters mirrored>)")
        sys.exit(1)

    mapping = mappings[sys.argv[1]]
    new_score = int(sys.argv[2])
    wordlist = sys.argv[3]

    with open(wordlist) as wordlist:
        for line in wordlist:
            word, score, *_ = line.split(';')

            score = int(score)

            for i in reversed(range(1, len(word)//2 + 1)):
                prefix = word[:len(word) - i*2]
                suffix = word[len(word) - i*2:][:i]
                mirrored = mirror(suffix.upper(), mapping)

                if mirrored and (prefix + suffix + mirrored).upper() == word.upper():
                    print(f"{prefix}{suffix};{new_score};{word} ({i})")

def mirror(word, mapping):
    if all(letter in mapping for letter in word):
        return ''.join(mapping[letter] for letter in reversed(word))
    else:
        return None

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__ == '__main__':
    main()

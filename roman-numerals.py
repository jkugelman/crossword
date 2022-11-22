#!/usr/bin/env python3

import fileinput
import sys

def count_hidden_numbers(phrase):
    spanning_numbers = {
        # 1
        'almoner',
        'amazonecho',
        'anemone',
        'auctione',
        'balcone',
        'balloone',
        'barone',
        'bayonet',
        'beckone',
        'boone',
        'buffoone',
        'cannone',
        'canone',
        'canyone',
        'cheone',
        'clooney',
        'comeoneileen',
        'component',
        'conedison',
        'coney',
        'coone',
        'corone',
        'crayone',
        'croone',
        'cronen',
        'demone',
        'easone',
        'errone',
        'exoner',
        'exponen',
        'geone',
        'goone',
        'hermione',
        'honed',
        'hones',
        'honey',
        'hormone',
        'ioned',
        'ioneer',
        'ioner',
        'ionesco',
        'irone',
        'krone',
        'lione',
        'looney',
        'lornadoone',
        'madrone',
        'mangione',
        'marathone',
        'marchione',
        'marione',
        'maroone',
        'mmone',
        'monet',
        'money',
        'moone',
        'nixone',
        'noneast',
        'noneed',
        'noneff',
        'nonel',
        'nonent',
        'noneq',
        'noness',
        'nonet',
        'nonev',
        'nonew',
        'nonex',
        'nooner',
        'oneals',
        'onearth',
        'onedge',
        'oneffect',
        'onegative',
        'onegg',
        'onegin',
        'oneida',
        'oneill',
        'onelm',
        'onempty',
        'onend',
        'onengine',
        'onerous',
        'onesia',
        'onette',
        'onews',
        'onex',
        'onevery',
        'peroneal',
        'pheromone',
        'poltroone',
        'ponen',
        'ponese',
        'poone',
        'positrone',
        'psychone',
        'quinone',
        'reckone',
        'renonev',
        'ronett',
        'roney',
        'rooney',
        'runyonesque',
        'ryanoneal',
        'salmone',
        'schoone',
        'sergioleone',
        'shaquilleoneal',
        'soned',
        'soner',
        'soonenough',
        'sooner',
        'strone',
        'tatumoneal',
        'tenoned',
        'tenoner',
        'tione',
        'tooned',
        'tooner',
        'toonew',
        'tronell',
        'weaponed',
        'whoneed',
        'whonever',

        # 2
        'justwow',
        'outwore',
        'outworn',
        'twoman',
        'twomen',
        'twonder',
        'twont',
        'twood',
        'tword',
        'twork',
        'tworld',
        'tworm',
        'tworn',
        'tworried',
        'tworry',
        'tworst',
        'tworth',
        'twould',
        'twound',

        # 3
        'earthreent',
        'worthreese',
        'northreef',
        'smoothreent',
        'southreef',

        # 4
        'ofour',

        # 5
        'chanelofive',
        'ifive',

        # 6

        # 7
        'breakseven',
        'drawseven',
        'getseven',
        'newsevent',
        'salesevent',
        'sevening',
        'seventura',
        'shipseven',

        # 8

        # 9
        'beninempire',
        'beninese',
        'niness',
        'bornineastla',
        'burnineffigy',
        'nineveh',

        # 10

        # 11
        'parallelevent',
    }

    hidden_numbers = {
        # 1
        'airfone',
        'antwone',
        'aproned',
        'ashcone',
        'bone',
        'capone',
        'chaperone',
        'cone',
        'corleone',
        'cortisone',
        'done',
        'drone',
        'gone',
        'jones',
        'lone',
        'mascarpone',
        'millhone',
        'navarone',
        'simone',
        'none',
        'outshone',
        'phone',
        'perone',
        'postpone',
        'prone',
        'ramone',
        'rehone',
        'rhone',
        'scone',
        'shoshone',
        'sierraleone',
        'simone',
        'stone',
        'symone',
        'throne',
        'toblerone',
        'tone',
        'tyrone',
        'zone',

        # 2

        # 3

        # 4
        'fourier',

        # 5

        # 6

        # 7

        # 8
        'deighton',
        'freight',
        'height',
        'leighton',
        'sleight',
        'weight',

        # 9
        'adenine',
        'alanine',
        'apennine',
        'arginine',
        'asinine',
        'atnine',
        'backnine',
        'borgnine',
        'canine',
        'dcnine',
        'eponine',
        'ernestborgnine',
        'feminine',
        'guanine',
        'janine',
        'jeanine',
        'leonine',
        'methionine',
        'mezzanine',
        'onine',
        'phenylalanine',
        'quinine',
        'ranine',
        'saturnine',
        'stanine',
        'strychnine',
        'threonine',
        'thyronine',
        'unfeminine',

        # 10
        'tenant',
        'tence',
        'tent',
    }

    for sn in spanning_numbers:
        phrase = phrase.replace(sn, 'S')

    for hn in hidden_numbers:
        phrase = phrase.replace(hn, 'H')

    return phrase.count('S'), phrase.count('H')

def main():
    assert words_to_numbers('noneexistent') == ['n', 1, 'exis', 10, 't']
    assert words_to_numbers('nineteeneightyfour') == [19, 84]
    assert words_to_numbers('fourthousandthreehundredandtwentyone') == [4321]

    assert bonus_score('ultramathoners') == 100
    assert bonus_score('vitocorleone') == 50

    for line in fileinput.input():
        phrase, score = line.strip().split(';')
        score = int(score)
    # 50 points per non-hidden number.
    phrase = words_to_numbers(phrase)
    score += sum(50 for word in phrase if type(word) == int)


        phrase = [to_roman(word) if type(word) == int else word for word in phrase]
        phrase = ''.join(str(word) for word in phrase)
        print(f"{phrase};{score}")

def words_to_numbers(phrase):
    numerals = {
        'athousandand': 1000,
        'athousand': 1000,
        'thousandand': 1000,
        'thousand': 1000,
        'ahundredand': 100,
        'ahundred': 100,
        'hundredand': 100,
        'hundred': 100,
        'ninety': 90,
        'eighty': 80,
        'seventy': 70,
        'sixty': 60,
        'fifty': 50,
        'fourty': 40,
        'forty': 40,
        'thirty': 30,
        'twenty': 20,
        'nineteen': 19,
        'eighteen': 18,
        'seventeen': 17,
        'sixteen': 16,
        'fifteen': 15,
        'fourteen': 14,
        'thirteen': 13,
        'twelve': 12,
        'eleven': 11,
        'ten': 10,
        'nine': 9,
        'eight': 8,
        'seven': 7,
        'six': 6,
        'five': 5,
        'four': 4,
        'three': 3,
        'two': 2,
        'one': 1,
    }

    phrase = [phrase]

    for numeral, number in numerals.items():
        for i, word in reversed(list(enumerate(phrase))):
            if type(word) == int:
                continue
            if numeral in word:
                phrase[i:i+1] = intersperse(word.split(numeral), number)

    phrase = [word for word in phrase if word != '']
    phrase = merge_adjacent_numbers(phrase)

    return phrase

def intersperse(words, number):
    words = iter(words)
    yield next(words)
    for word in words:
        yield number
        yield word

def merge_adjacent_numbers(phrase):
    # Merge thousand and hundred multipliers.
    i = 0
    while i < len(phrase) - 1:
        a, b = phrase[i], phrase[i + 1]
        if type(a) == int and type(b) == int:
            if len(str(a)) == 1 and b in {1000, 100}:
                phrase[i:i+2] = [a * b]
                continue
        i += 1

    # Add adjacent numbers.
    i = 0
    while i < len(phrase) - 1:
        a, b = phrase[i], phrase[i + 1]
        if type(a) == int and type(b) == int:
            if str(a)[-len(str(b)):].strip('0') == '':
                phrase[i:i+2] = [a + b]
                continue
        i += 1

    return phrase

def to_roman(n):
    mapping = [
        ('m', 1000),
        ('cm', 900),
        ('d', 500),
        ('cd', 400),
        ('c', 100),
        ('xc', 90),
        ('l', 50),
        ('xl', 40),
        ('x', 10),
        ('ix', 9),
        ('v', 5),
        ('iv', 4),
        ('i', 1),
    ]

    if n not in range(1, 5001):
        return str(n)

    result = ""
    for numeral, integer in mapping:
        while n >= integer:
            result += numeral
            n -= integer
    return result

if __name__ == '__main__':
    main()

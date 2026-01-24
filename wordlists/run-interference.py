#!/usr/bin/env python3

# Collab with Adam Wagner.
# Figures out which meta answers can be spelled for our RUN INTERFERENCE puzzle.

import orjson
from pprint import pprint

from lib import grouped_by, is_symmetrical, spell_meta

def main():
    metas = {
        'abet',
        'assist',
        'bait',
        'bar',
        'blip',
        'block',
        'bump',
        'cold',
        'cramp',
        'deny',
        'deter',
        'fail',
        'flub',
        'foil',
        'foul',
        'halt',
        'help',
        'hold',
        'jam',
        'loss',
        'rain',
        'run',
        'slip',
        'snag',
        'stall',
        'stop',
        'trip',
    }

    themers = {
        themer: letter
        for themer, letter in (
            line.strip().split(',')
            for line in open('run-interference.csv')
        )
        if len(themer) <= 15
    }

    results = {meta: run_interference(themers, meta) for meta in metas}

    def default(obj):
        if isinstance(obj, set):
            return list(obj)
        raise TypeError
    print(orjson.dumps(
        results,
        option=orjson.OPT_NON_STR_KEYS | orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS,
        default=default
    ).decode())

def run_interference(themers, meta):
    metas = (
        tuple(
            c
            for t in spell_meta(meta, themers)
            for c in ([*t, 'runinterference'],)
            if is_symmetrical(c)
        ),
        tuple(
            c
            for t in spell_meta(meta, themers)
            for c in (
                ([*t[:len(t)//2], 'runinterference', *t[len(t)//2:]],)
                if len(t) % 2 == 0 else ()
            )
            if is_symmetrical(c)
        ),
    )

    return {
        j: (
            [
                dict(grouped_by(tuple(t[i] for t in metas[j]), len))
                for i in range(len(metas[j][0]))
            ]
            if metas[j] else []
        )
        for j in range(len(metas))
    }

if __name__ == '__main__':
    main()

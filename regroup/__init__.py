
from collections import Counter
from functools import reduce
from itertools import groupby
import re

from marisa_trie import Trie


class Patt:
    #EXACT = 0
    DIGIT = 1
    SPACE = 2
    #NONSPACE = 3
    WORD  = 3

Patt.all = [
    (Patt.DIGIT, '[0-9]'),
    (Patt.SPACE, ' '),
]


# NOTE: aha, use a trie of regex matches

def make_trie(words):
    root = dict()
    for word in words:
        current_dict = root
        for letter in word:
            current_dict = current_dict.setdefault(letter, {})
        current_dict[None] = None
    return root


class Pattern:

    def __init__(self, s):
        self.s = s
        # matrix of all patterns that match each character
        self.chars = set(s)
        self.charmatches = [(p, [bool(re.match(p, c)) for c in s])
                                for flag, p in Patt.all]
        '''
        self.seqs = [(p, [(x, len(list(y)))
                        for x, y in groupby(bools)])
                            for p, bools in self.charmatches]
        '''
        self.seqs = self.charmatches
        # favor fewer true/false sequences
        self.seqs = sorted(self.seqs, key=lambda x: len(x[1]))

        self.pattern = self.get_pattern()

    def get_pattern(self):
        '''for each character, use the first pattern that matches is'''
        patterns = []
        for i, c in enumerate(self.s):
            p = re.escape(c)
            for pat, seq in self.seqs:
                if seq[i]:
                    p = pat
                    break
            patterns.append(p)

        groups = [(k, len(list(v))) for k, v in groupby(patterns)]
        grouped = ['{}{{{}}}'.format(k, v).replace('{1}', '')
                        for k, v in groups]
        return ''.join(grouped)

    def __repr__(self):
        return 's={} pattern={} seqs={}'.format(
            repr(self.s), repr(self.pattern), repr(self.seqs))


def match(values):

    if not values:
        return None

    valcnts = Counter(values)
    if len(valcnts) == 1:
        return list(valcnts.keys())[0]

    chars = {k: Pattern(k) for k in valcnts.keys()}

    from pprint import pprint
    # pprint(chars)

    patterns = [v.pattern for v in chars.values()]
    patset = sorted(set(patterns))

    print(make_trie(values))

    if len(patset) == 1:
        return patset[0]

    return '(' + '|'.join(patset) + ')'

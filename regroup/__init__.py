
from collections import Counter, defaultdict
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

def trie_make(words):
    root = dict()
    for word in words:
        current_dict = root
        for letter in word:
            current_dict = current_dict.setdefault(letter, {})
        current_dict[''] = {}
    return root


def dawg_make(d):
    if len(d) == 1:
        k, v = list(d.items())[0]
        v = dawg_make(v)
        if v and isinstance(v, dict) and len(v) == 1:
            k2, v2 = list(v.items())[0]
            if k2:
                return {k + k2: v2}
        return d
    else:
        return {k: dawg_make(v) if v else v
                    for k, v in d.items()}



def all_len1(l):
    return all(len(k) == 1 for k in l)


def all_values_not(d):
    return all(not v or v == {'': {}} for v in d.values())


def is_char_class(d):
    return (all_len1(d.keys())
            and all_values_not(d))


def all_suffixes_identical(d):
    vals = list(d.values())
    return len(vals) > 1 and len(set(map(str, vals))) == 1


def is_optional(d):
    items = sorted(list(d.items()))
    if len(items) == 2:
        print('items', items)
        return not items[0][0] and not items[1][1] or items[1][1] == {'': {}}
    return False


def all_len01(l):
    return set(map(len, l)) == {0, 1}


def is_optional_char_class(d):
    return (all_len01(d.keys())
            and all_values_not(d))


def condense_range(digits):
    digits = sorted(int(d) for d in digits if d)
    l = []
    while digits:
        # print('digits', digits)
        i = 1
        while i < len(digits):
            if digits[i] != digits[i - 1] + 1:
                break
            i += 1
        if i <= 1:
            l.append(str(digits[0]))
        elif i == 2:
            l.append('{}{}'.format(digits[0], digits[1]))
        else:
            l.append('{}-{}'.format(digits[0], digits[i - 1]))
        if i == len(digits):
            digits = []
        else:
            del digits[:i]
    return ''.join(l)


def suffixes(d):
    # match up keys with same values
    return sorted(((k, [a for a, _ in v])
                    for k, v in groupby(sorted(d.items(),
                                               key=lambda x: repr(x[0])),
                                        key=lambda x: x[1])),
                   key=lambda x: (repr(x[1]), repr(x[0])))


def as_charclass(l):
    # s = ''.join(sorted(l))
    s = condense_range(l)
    if len(l) > 1:
        s = '[' + s + ']'
    return s


def as_opt_charclass(l):
    s = ''.join(sorted(l))
    if len(l) > 1:
        s = '[' + s + ']'
    s += '?'
    return s


def as_group(l):
    l = list(l)
    s = '|'.join(sorted(l))
    if len(l) > 1:
        s = '(' + s + ')'
    return s


def repr_keys(l):
    if all_len1(l):
        return as_charclass(l)
    if all_len01(l):
        return as_opt_charclass(l)
    return as_group(l)


def group(s):
    if '|' in s:
        s = '(' + s + ')'
    return s


def dawg_dump(d):
    # print('dawg_dump', d)
    if d and len(d) > 1 and is_char_class(d):
        s = '[' + ''.join(sorted(d.keys())) + ']'
    elif d and all_suffixes_identical(d):
        print('all_suffixes_identical', d)
        # condense suffixes from multiple keys within a subtree
        v = list(d.values())[0]
        if len(d) > 1 and all_len1(d):
            s = '[' + ''.join(sorted(d.keys())) + ']'
        elif is_optional(d):
            print('is_optional', d)
            s = re.escape(sorted(list(d.keys()))[1]) + '?'
        elif is_optional_char_class(d):
            s = '[' + ''.join(sorted(d.keys())) + ']?'
        else:
            s = '|'.join(k for k in sorted(d.keys()))
            if len(d) > 1:
                s = '(' + s + ')'
        s += dawg_dump(v)
    elif is_optional(d):
        print('is_optional', d)
        s = re.escape(sorted(list(d.keys()))[1]) + '?'
    elif is_optional_char_class(d):
        s = '[' + condense_range(d.keys()) + ']?'
    else:
        bysuff = suffixes(d)
        print('suffixes', bysuff)
        if len(bysuff) < len(d):
            # at least one suffix shared
            s = '|'.join(group(repr_keys(k) + dawg_dump(v))
                            for v, k in bysuff)
            if len(bysuff) > 1:
                s = '(' + s + ')'
        else:
            s = '|'.join(k + (dawg_dump(v) if v else '')
                                for k, v in sorted(d.items()))
            if len(d) > 1:
                s = '(' + s + ')'
    return s


def match(values):

    if not values:
        return None

    print('values', values)
    print('trie', trie_make(values))
    print('dawg', dawg_make(trie_make(values)))
    # print('dawg2', dawg_dump(trie_make(values)))
    print('dawg3', dawg_dump(dawg_make(trie_make(values))))

    return dawg_dump(dawg_make(trie_make(values)))


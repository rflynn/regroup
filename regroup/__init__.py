# vim: set ts=4 et:

from collections import Counter, defaultdict
from copy import copy
from functools import reduce
from itertools import groupby
from pprint import pprint, pformat
import re

# relative imports
from .tokenizer import Tokenizer, DictionaryTokenizer, Tagged, TaggingTokenizer
from .relax import suffixes_diff, dict_merge


def match(strings):
    '''
    convenience wrapper for generating one regex from a list of strings
    '''
    return DAWG.from_iter(strings).serialize()


class StringSet:

    '''
    a set of strings
    instead of using a list of strings everywhere, condense duplicates and preserve additional
    statistics so we can use less memory, avoid repetitive calculations and make better decisions
    '''

    def __init__(self, strings=None):
        strings = strings or []
        self.strings = Counter(strings)

    def __iter__(self):
        return iter(self.strings.keys())


class TaggedString:

    def __init__(self, string, tokenizer=None):
        tokenizer = tokenizer or Tokenizer()
        self.string = string
        self.tagged = [t for t in tokenizer.tokenize(string)]

    def __repr__(self):
        return repr(self.tagged)


class Trie:

    '''
    Trie
    an n-ary string character tree
    ref: https://en.wikipedia.org/wiki/Trie
    '''

    def __init__(self, stringset=None, tokenizer=None):
        stringset = stringset or StringSet()
        self.tokenizer = tokenizer or Tokenizer()
        self.trie = self._build(stringset)

    @classmethod
    def from_iter(cls, strings):
        return cls(stringset=StringSet(strings))

    @classmethod
    def from_list(cls, strings):
        return cls.from_iter(strings)

    def __repr__(self):
        return pformat(self.trie)

    def __dict__(self):
        return self.trie

    def items(self):
        return self.trie.items()

    def keys(self):
        return self.trie.keys()

    def values(self):
        return self.trie.values()

    def _build(self, strings):
        root = {}
        for word in strings:
            d = root
            for token in self.tokenizer.tokenize(word):
                d = d.setdefault(token, {})
            # NOTE: all these empty dictionaries cost memory
            # consider trading simplicity of implementation for efficiency by refactoring to None
            d[''] = {}  # denote end-of-string
        return root


class DAWG:

    '''
    Directed Acyclic Word Graph
    like a Trie, but we condense substrings and share substrings/suffixes where possible
    ref: https://en.wikipedia.org/wiki/Deterministic_acyclic_finite_state_automaton
    '''

    def __init__(self, trie=None):
        self.dawg = DAWG._build(trie)

    @classmethod
    def from_iter(cls, strings):
        return cls(trie=Trie(StringSet(strings)))

    @classmethod
    def from_list(cls, strings):
        return cls.from_iter(strings)

    @classmethod
    def from_trie(cls, t):
        return cls(trie=t)

    @classmethod
    def from_dawg(cls, d):
        x = cls(trie={})
        x.dawg = d
        return x

    def __repr__(self):
        return pformat(self.dawg)

    def __dict__(self):
        return self.trie

    def items(self):
        return self.dawg.items()

    def keys(self):
        return self.dawg.keys()

    def values(self):
        return self.dawg.values()

    @classmethod
    def _build(cls, t):

        # FIXME: for a real DAWG, we need to handle shared suffixes for strings with different prefixes

        # return dict(t.trie)
        made = {}
        for k, v in t.items():
            v = cls._build(v)
            # merge substrings
            if k and len(v) == 1 and '' not in v:
                k2, v2 = list(v.items())[0]
                made[k + k2] = v2
            else:
                made[k] = v
        return made

    def flatten(d, clusters=None):
        return DAWG._flatten(d, '')

    @classmethod
    def _flatten(cls, d, path):
        for k, v in sorted(d.items()):
            if k:
                yield from cls._flatten(v, path + k)
            else:
                yield path

    def cluster_by_prefixlen(self, length):
        clusters = []
        DAWG._cluster_by_prefixlen(length, clusters, self.dawg, '')
        if not clusters:
            clusters = [('', self.dawg)]
        return clusters

    @classmethod
    def _cluster_by_prefixlen(cls, length, clusters, d, path):
        for k, v in sorted(d.items()):
            path2 = path + k
            if len(path2) >= length:
                # the length of the prefix we've seen meets or exceeds the prefix
                # length, so consider everything below this as a group
                clusters.append((path2, v))
            elif not v:
                # path is shorter than specified length
                # include it
                clusters.append((path2, {}))
            else:
                cls._cluster_by_prefixlen(length, clusters, v, path2)

    def dawg_weights(d, l):
        """given a DAWG and the original list, calculate weights at each branchpoint"""
        weights = defaultdict(int)
        _dawg_weights(l, weights, d, [])
        return dict(weights)

    def _dawg_weights(l, weights, d, path):
        for k, v in d.items():
            path2 = path + [k]
            path2str = ''.join(path)
            weights[tuple(path2)] += sum(1 for x in l if x.startswith(path2str))
            _dawg_weights(l, weights, v, path2)

    def top_weights(weights, n):
        wsorted = sorted(weights.items(),
                         key=lambda x: x[1],
                         reverse=True)
        pprint(wsorted)
        top = {}
        for k, v in wsorted:
            # if there's a prefix of k in top, remove it
            remove = [t for t in top
                      if k[0:len(t)] == t]
            for r in remove:
                del top[r]
            top[k] = v
            if len(top) == n:
                break
        return top

    def serialize(self):
        return DAWG.serialize_regex(self.dawg)

    @classmethod
    def _serialize(cls, dawg):
        return cls.serialize_regex(dawg)

    @classmethod
    def serialize_regex(cls, d, level=0):
        # pprint(d)
        if d and is_char_class(d):
            s = as_char_class(d.keys())
        elif d and all_suffixes_identical(d):
            # print('all_suffixes_identical', d)
            # condense suffixes from multiple keys within a subtree
            v = list(d.values())[0]
            # print('v', v)
            if all_len1(d):
                s = as_charclass(d.keys())
            elif is_optional_char_class(d):
                s = as_opt_charclass(d.keys())
            elif is_optional(d):
                s = as_optional_group(d.keys())
                # s = re.escape(sorted(list(d.keys()))[1]) + '?'
            else:
                s = as_group(d.keys())
            s += cls.serialize_regex(v, level=level + 1)
        elif is_optional_char_class(d):
            s = as_opt_charclass(d.keys())
        elif is_optional(d):
            # print('is_optional', d)
            s = opt_group(re.escape(sorted(list(d.keys()))[1])) + '?'
            # s = as_optional_group(d.keys())
        else:
            bysuff = suffixes(d)
            # print('suffixes', bysuff)
            if len(bysuff) < len(d):
                # at least one suffix shared
                # print('shared suffix', bysuff)
                # print('level=', level)
                suffixed = [repr_keys(k, do_group=(level > 0)) +
                            cls.serialize_regex(v, level=level + 1)
                            for v, k in bysuff]
                # print('suffixed', suffixed)
                s = group(suffixed)
            else:
                grouped = [k + (cls.serialize_regex(v, level=level + 1) if v else '')
                           for k, v in sorted(d.items())]
                # print('grouped', grouped)
                s = group(grouped)
        return s


def all_len1(l):
    return all(len(k) == 1 for k in l)


def all_values_not(d):
    return all(not v or v == {'': {}} for v in d.values())


def is_char_class(d):
    return (all_len1(d.keys()) and
            all_values_not(d))


def as_char_class(strings):
    s = ''.join(sorted(strings))
    if len(s) > 1:
        s = '[' + s + ']'
    return s


def all_suffixes_identical(d):
    vals = list(d.values())
    return len(vals) > 1 and len(set(map(str, vals))) == 1


def is_optional(d):
    if len(d) == 2:
        items = sorted(list(d.items()))
        # print('is_optional items', items)
        return (not items[0][0] and (
                not items[1][1] or items[1][1] == {'': {}}))
    return False


def is_optional_strings(strings):
    return not all(s for s in strings)


def as_optional_group(strings):
    strings = sorted(strings)
    # print('as_optional_group:', strings)
    assert strings[0] == ''
    j = strings[1:]
    if not j:
        return ''
    s = '|'.join(j)
    if len(j) > 1 or len(j[0]) > 1 or s.endswith('?') or '|' in s or '(' in s:
        s = '(' + s + ')'
    s += '?'
    return s


def all_len01(l):
    return set(map(len, l)) == {0, 1}


def is_optional_char_class(d):
    return (all_len01(d.keys()) and
            all_values_not(d))


def condense_range(chars):
    # NOTE: eliminate zero-length strings
    # it's up to callers to note whether char classes are optional
    chars = sorted([c for c in chars if c])
    l = []
    while chars:
        i = 1
        while i < len(chars):
            if chars[i] != chr(ord(chars[i - 1]) + 1):
                break
            i += 1
        if i <= 1:
            l.append(str(chars[0]))
        elif i == 2:
            l.append('{}{}'.format(chars[0], chars[1]))
        else:
            l.append('{}-{}'.format(chars[0], chars[i - 1]))
        if i == len(chars):
            chars = []
        else:
            del chars[:i]
    return ''.join(l)


def emptyish(x):
    '''collapse empty strings'''
    if not x or x == {'': {}}:
        return {}
    return x


def suffixes(d):
    # match up keys with same values
    return sorted(((k, [a for a, _ in v])
                  for k, v in groupby(sorted(d.items(),
                                             key=lambda x: repr(emptyish(x[0]))),
                                      key=lambda x: emptyish(x[1]))),
                  key=lambda x: (repr(x[1]), repr(x[0])))


def as_charclass(l):
    # s = ''.join(sorted(l))
    s = condense_range(l)
    if len(l) > 1:
        s = '[' + s + ']'
    return s


def as_opt_charclass(l):
    s = condense_range(l)
    if len(l) > 2:
        s = '[' + s + ']'
    else:
        s = re.escape(s)
    s += '?'
    return s


def as_group(l, do_group=True):
    l = sorted(l)
    # print('as_group', l)
    suffix = longest_suffix(l) if len(l) > 1 else ''
    # print('suffix', suffix)
    if suffix:
        lensuff = len(suffix)
        prefixes = [x[:-lensuff] for x in l]
        if all_len1(prefixes):
            s = as_char_class(prefixes)
        else:
            s = group(prefixes)
        s += suffix
    else:
        # print('as_group', l)
        s = group(l, do_group=do_group)
    return s


def repr_keys(l, do_group=True):
    # print('repr_keys', l)
    if all_len1(l):
        return as_charclass(l)
    if all_len01(l):
        return as_opt_charclass(l)
    return as_group(l, do_group=do_group)


def group(strings, do_group=True):
    # print('group', strings)
    if is_optional_strings(strings):
        return as_optional_group(strings)
    s = '|'.join(strings)
    if do_group and (len(strings) > 1 or ('|' in s and '(' not in s)):
        # print('group', s)
        s = '(' + s + ')'
    # else:
    #    print('no group', strings, do_group, len(strings))
    return s


def longest_prefix(strings):
    if not strings:
        return ''
    prefix = strings[0]
    # initialize with longest possible result, then work down
    # if we hit zero, we're done
    longest = min(len(s) for s in strings)
    for i in range(1, len(strings)):
        longest = longest_prefix_2strings(prefix, strings[i], longest)
        if longest == 0:
            return ''
    return prefix[:longest][::-1]


def longest_prefix_2strings(x, y, longest):
    length = min(min(len(x), len(y)), longest)
    for i in range(1, length + 1):
        if x[:i] != y[:i]:
            return i - 1
    return length


def longest_suffix(strings):
    return longest_prefix([s[::-1] for s in copy(strings)])


def opt_group(s):
    if len(s) - s.count('\\') > 1:
        # print('opt_group', s)
        s = '(' + s + ')'
    return s


class DAWGRelaxer:

    def __init__(self, dawg):
        self.dawg = dawg

    def relaxable(self):
        return DAWGRelaxer._relaxable(self.dawg.dawg)

    @classmethod
    def _relaxable(cls, d):
        diffcnt = suffixes_diff(d)
        if diffcnt:
            yield (diffcnt, d)
        for k, v in d.items():
            if len(v) > 1:
                yield from cls._relaxable(v)

    def relax(self, threshold=1):
        '''
        merge similar DAWG subtrees that differ by <= threshold members
        '''
        while True:
            rel = sorted(self.relaxable(), key=lambda x: (x[0], repr(x[1])))
            # pprint(rel)
            if rel and rel[0][0] <= threshold:
                relaxme = rel[0]
                relaxed = self.do_relax(relaxme[1])
                self.dawg = DAWG.from_dawg(relaxed)
            else:
                break
        return self.dawg

    def do_relax(self, d):
        merged = reduce(dict_merge, d.values(), {})
        d2 = {k: merged for k in d}
        # print('merged', merged)
        # print('d2', d2)
        return DAWGRelaxer._replace(self.dawg.dawg, d, d2)

    @classmethod
    def _replace(cls, dawg, find, replace):
        if dawg == find:
            return replace
        return {k: cls._replace(v, find, replace)
                for k, v in dawg.items()}

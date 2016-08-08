# vim: set ts=4 et:

from collections import Counter, defaultdict
from copy import copy
from itertools import groupby
from pprint import pprint, pformat
import re

from Levenshtein import distance as levenshtein


def match(strings):
    '''
    convenience wrapper for generating one regex from a list of strings
    '''
    return DAWG.from_list(strings).serialize()


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


def chars(string):
    for c in string:
        yield c


def tokenize_regex_case_sensitive(string):
    for token in re.findall('[a-z]+|[A-Z]+|\d+|\s+|.', string):
        yield token


class Tokenizer:
    def __init__(self):
        pass
    def tokenize(self, string):
        return chars(string)


class DictionaryTokenizer(Tokenizer):

    def __init__(self, wordset=None):
        wordset = wordset or set()
        self.wordset = wordset

    def tokenize(self, string):
        matchstring = string
        while matchstring:
            nexttoken = self.nexttoken(matchstring)
            yield string[:len(nexttoken)]
            matchstring = matchstring[len(nexttoken):]
            string = string[len(nexttoken):]

    def nexttoken(self, substr):
        longest = ''
        for word in self.wordset:
            if len(word) > len(longest) and substr.startswith(word):
                longest = word
        if not longest:
            return self.fallback(substr)
        return longest

    def fallback(self, string):
        m = re.search('^([a-z]+|[A-Z]+|\d+|\s+|.)', string)
        if m:
            return m.groups()[0]
        return string[0]


class Tagged:

    def __init__(self, string, tag):
        self.string = string
        self.tag = tag

    def __str__(self):
        return self.string

class TaggingTokenizer:

    def __init__(self, tags):
        self.tags = tags

    def tokenize(self, string):
        matchstring = string
        while matchstring:
            nexttoken, nexttag = self.nexttoken(matchstring)
            yield (nexttoken, nexttag)
            matchstring = matchstring[len(nexttoken):]
            string = string[len(nexttoken):]

    def nexttoken(self, substr):
        longest = ('', '')
        for tagname, tagdef in self.tags.items():
            match = self.tagmatch(substr, tagdef)
            if match and len(match) > len(longest[0]):
                longest = (match, tagname)
        if not longest[0]:
            longest = (self.fallback(substr), None)
        return longest

    def tagmatch(self, substr, tagdef):
        if isinstance(tagdef, (list, set)):
            for t in tagdef:
                if substr.startswith(t):
                    return substr[:len(t)]
        else:
            m = tagdef.search(substr)
            if m:
                sp = m.span()
                if sp[0] == 0:
                    return substr[:sp[1]]

    def fallback(self, string):
        m = re.search('^([a-z]+|[A-Z]+|\d+|\s+|.)', string)
        if m:
            return m.groups()[0]
        return string[0]



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
    '''

    def __init__(self, stringset=None, tokenizer=None):
        stringset = stringset or StringSet()
        self.tokenizer = tokenizer or Tokenizer()
        self.trie = self._build(stringset)

    @classmethod
    def from_list(cls, stringlist):
        return cls(stringset=StringSet(stringlist))

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
            #for letter in word:
            #    d = d.setdefault(letter, {})
            # NOTE: all these empty dictionaries cost memory
            # consider trading simplicity of implementation for efficiency by refactoring to None
            d[''] = {}  # denote end-of-string
        return root


class DAWG:

    '''
    Directed Acyclic Word Graph
    like a Trie, but we condense substrings and share substrings/suffixes where possible
    '''

    def __init__(self, trie=None):
        self.dawg = DAWG._build(trie)

    @classmethod
    def from_list(cls, stringlist):
        return cls(trie=Trie(StringSet(stringlist)))

    @classmethod
    def from_trie(cls, t):
        return cls(trie=t)

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
        made = {}
        for k, v in t.items():
            v = cls._build(v)
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
            if all_len1(d):
                s = as_charclass(d.keys())
            elif is_optional(d):
                # print('is_optional', d)
                s = re.escape(sorted(list(d.keys()))[1]) + '?'
            elif is_optional_char_class(d):
                s = as_opt_charclass(d.keys())
            else:
                s = as_group(d.keys(), level=level)
            s += cls.serialize_regex(v, level=level+1)
        elif is_optional(d):
            # print('is_optional', d)
            s = opt_group(re.escape(sorted(list(d.keys()))[1])) + '?'
        elif is_optional_char_class(d):
            s = as_opt_charclass(d.keys())
        else:
            bysuff = suffixes(d)
            # print('suffixes', bysuff)
            if len(bysuff) < len(d):
                # at least one suffix shared
                # print('shared suffix', bysuff)
                suffixed = [repr_keys(k, level=level) + cls.serialize_regex(v, level=level+1)
                                for v, k in bysuff]
                s = group(suffixed, level=level)
            else:
                grouped = [k + (cls.serialize_regex(v, level=level+1) if v else '')
                                    for k, v in sorted(d.items())]
                s = group(grouped, level=level)
        return s


def all_len1(l):
    return all(len(k) == 1 for k in l)


def all_values_not(d):
    return all(not v or v == {'': {}} for v in d.values())


def is_char_class(d):
    return (all_len1(d.keys())
            and all_values_not(d))


def as_char_class(strings):
    s = ''.join(sorted(strings))
    if len(s) > 1:
        s = '[' + s + ']'
    return s


def all_suffixes_identical(d):
    vals = list(d.values())
    return len(vals) > 1 and len(set(map(str, vals))) == 1


def is_optional(d):
    items = sorted(list(d.items()))
    if len(items) == 2:
        # print('is_optional items', items)
        return (not items[0][0] and (
                not items[1][1] or items[1][1] == {'': {}}))
    return False


def all_len01(l):
    return set(map(len, l)) == {0, 1}


def is_optional_char_class(d):
    return (all_len01(d.keys())
            and all_values_not(d))


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
    # s = ''.join(sorted(l))
    s = condense_range(l)
    if len(l) > 1:
        s = '[' + s + ']'
    s += '?'
    return s


def as_group(l, level=0):
    l = sorted(l)
    suffix = longest_suffix(l) if len(l) > 1 else 0
    if suffix:
        lensuff = len(suffix)
        prefixes = [x[:-lensuff] for x in l]
        if all_len1(prefixes):
            s = as_char_class(prefixes)
        else:
            s = group(prefixes, level=level)
        s += suffix
    else:
        s = group(l)
    return s


def repr_keys(l, level=0):
    if all_len1(l):
        return as_charclass(l)
    if all_len01(l):
        return as_opt_charclass(l)
    return as_group(l, level=level)


def group(strings, level=0):
    s = '|'.join(strings)
    if len(strings) > 1:
        s = '(' + s + ')'
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
    return prefix[:longest]


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


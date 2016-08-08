
from collections import Counter, defaultdict
from functools import reduce
from itertools import groupby
from pprint import pprint
import re

from Levenshtein import distance as levenshtein


def trie_make(words):
    root = {}
    for word in words:
        d = root
        for letter in word:
            d = d.setdefault(letter, {})
        d[''] = {}
    return root


def dawg_make(d):
    made = {}
    for k, v in d.items():
        v = dawg_make(v)
        if k and len(v) == 1 and '' not in v:
            k2, v2 = list(v.items())[0]
            made[k + k2] = v2
        else:
            made[k] = v
    return made
            

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
        print('is_optional items', items)
        return (not items[0][0] and (
                not items[1][1] or items[1][1] == {'': {}}))
    return False


def all_len01(l):
    return set(map(len, l)) == {0, 1}


def is_optional_char_class(d):
    return (all_len01(d.keys())
            and all_values_not(d))


def condense_range(chars):
    chars = sorted(int(d) for d in chars if d)
    l = []
    while chars:
        # print('chars', chars)
        i = 1
        while i < len(chars):
            if chars[i] != chars[i - 1] + 1:
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


def opt_group(s):
    if len(s) - s.count('\\') > 1:
        s = '(' + s + ')'
    return s


def dawg_dump(d):
    pprint(d)
    if d and len(d) > 1 and is_char_class(d):
        s = '[' + ''.join(sorted(d.keys())) + ']'
    elif d and all_suffixes_identical(d):
        print('all_suffixes_identical', d)
        # condense suffixes from multiple keys within a subtree
        v = list(d.values())[0]
        if len(d) > 1 and all_len1(d):
            s = as_charclass(d.keys())
        elif is_optional(d):
            print('is_optional', d)
            s = re.escape(sorted(list(d.keys()))[1]) + '?'
        elif is_optional_char_class(d):
            s = as_opt_charclass(d.keys())
        else:
            s = as_group(d.keys())
        s += dawg_dump(v)
    elif is_optional(d):
        print('is_optional', d)
        s = opt_group(re.escape(sorted(list(d.keys()))[1])) + '?'
    elif is_optional_char_class(d):
        s = as_opt_charclass(d.keys())
    else:
        bysuff = suffixes(d)
        # print('suffixes', bysuff)
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


def dawg_flatten(d, clusters=None):
    return _dawg_flatten(d, '')


def _dawg_flatten(d, path):
    for k, v in sorted(d.items()):
        if k:
            yield from _dawg_flatten(v, path + k)
        else:
            yield path


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


def dawg2regex(d, cluster=None):
    raise NotImplementedError




class Cluster:
    def __init__(self):
        self.left = None
        self.dist = None
        self.right = None
    def __repr__(self):
        return '({} {} {})'.format(self.left, self.dist, self.right)
    def dump(self, indent=0):
        if isinstance(self.left, str):
            print(' ' * indent, self.left)
        else:
            self.left.dump(indent=indent+1)
        print(' ' * indent, self.dist)
        if isinstance(self.right, str):
            print(' ' * indent, self.right)
        else:
            self.right.dump(indent=indent+1)
    def __iter__(self):
        yield self
        if isinstance(self.left, Cluster):
            yield from self.left
        if isinstance(self.right, Cluster):
            yield from self.right
    def clusters_by(self, dist):
        if self.dist <= dist:
            return [(c.left, c.right)
                        for c in iter(self)
                            if isinstance(c.left, str)]
        else:
            return (self.left.clusters_by(dist),
                    self.right.clusters_by(dist))
    def add(self, clusters, grid, lefti, righti):
        self.left = clusters[lefti]
        self.right = clusters[righti]
        self.dist = sorted(grid[lefti])[1]
        # merge columns grid[row][righti] and row grid[righti] into corresponding lefti
        for r in grid:
            r[lefti] = min(r[lefti], r.pop(righti))
        grid[lefti] = list(map(min, zip(grid[lefti], grid.pop(righti))))
        clusters.pop(righti)
        return (clusters, grid)


def agglomerate(labels, grid):
    """
    given a list of labels and a 2-D grid of distances, iteratively agglomerate
    hierarchical Cluster
    """
    clusters = labels
    while len(clusters) > 1:
        # find 2 closest clusters
        # print(clusters)
        distances = [(1, 0, grid[1][0])]
        for i, row in enumerate(grid[2:]):
            distances += [(i + 2, j, c) for j, c in enumerate(row[:i+2])]
        j, i, _ = min(distances, key=lambda x: x[2])
        # merge i<-j
        c = Cluster()
        clusters, grid = c.add(clusters, grid, i, j)
        clusters[i] = c
    return clusters.pop()


def strdist(x, y, toks):
    tx = toks[x]
    ty = toks[y]
    return (sum(1 for t in tx if t not in ty) +
            sum(1 for t in ty if t not in tx))


def tokenize(w):
    return re.findall('[a-z]+|[A-Z]+|\d|.', w)
    

def cluster_input(l):

    tokens = {w: tokenize(w) for w in l}
    dist = []
    for i, x in enumerate(l):
        d = [strdist(x, y, tokens)
                for j, y in enumerate(l)]
        dist.append(d)

    clusters = agglomerate(l, dist)
    distances = [node.dist for node in clusters]
    distcnt = len(distances)
    distsum = sum(distances)
    distmean = distsum / distcnt
    print('distcnt={} distsum={} distmean={:.2f} distances={}'.format(
        distcnt, distsum, distmean, distances))
    return clusters


def match(values):

    if not values:
        return None

    print('values', values)
    print('trie', trie_make(values))
    print('dawg', dawg_make(trie_make(values)))
    # print('dawg2', dawg_dump(trie_make(values)))
    print('dawg3', dawg_dump(dawg_make(trie_make(values))))

    return dawg_dump(dawg_make(trie_make(values)))


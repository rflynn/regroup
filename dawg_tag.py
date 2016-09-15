
'''
if we know what our strings will be in advance,
we can define tags to identify substrings that belong to the same set
such that strings with substrings in the same tags group similarly
'''

from collections import defaultdict
from pprint import pprint
import re

from regroup import TaggingTokenizer, TaggedString

strings = [
    'EFgreen',
    'EFgrey',
    'EntireS1',
    'EntireS2',
    'J27GreenP1',
    'J27GreenP2',
    'J27RedP1',
    'J27RedP2',
    'JournalP1Black',
    'JournalP1Blue',
    'JournalP1Green',
    'JournalP1Red',
    'JournalP2Black',
    'JournalP2Blue',
    'JournalP2Green',
]


print('strings:')
pprint(strings)

# ref: https://en.wikipedia.org/wiki/Part-of-speech_tagging
tags = {
    '$color': set('Black Blue Green Red'.split()),
    '$number': re.compile('\d+'),
}
print('tags:')
pprint(tags, width=1)

tok = TaggingTokenizer(tags)
tagged = [TaggedString(s, tokenizer=tok) for s in strings]
print('strings tokenized and tagged:')
pprint(tagged)

print('group lists of tokens by pattern of (tag or token):')
clusters = defaultdict(list)
for t in tagged:
    tagpattern = tuple((tag or tok) for tok, tag in t.tagged)
    toks = [tok for tok, tag in t.tagged]
    clusters[tagpattern].append(toks)
clusters = dict(clusters)
pprint(clusters, width=120)


def group(words):
    s = ','.join(sorted(words))
    if len(words) > 1:
        s = '[' + s + ']'
    return s


print('describe all strings whose pattern is seen 2+ times:')
for pattern, stringparts in sorted(clusters.items()):
    if len(stringparts) > 1:
        patset = [set() if p in tags else p for p in pattern]
        for strings in stringparts:
            for i, part in enumerate(strings):
                if isinstance(patset[i], set):
                    patset[i].add(part)
        patstr = ''.join(group(p) if isinstance(p, set) else p for p in patset)
        print(patstr)

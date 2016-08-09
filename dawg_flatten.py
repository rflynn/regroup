
from pprint import pprint

from regroup import DAWG, DAWGRelaxer


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

strings = 'Alabama · Alaska · Arizona · Arkansas · California · Colorado · Connecticut · Delaware · Florida · Georgia · Hawaii · Idaho · Illinois · Indiana · Iowa · Kansas · Kentucky · Louisiana · Maine · Maryland · Massachusetts · Michigan · Minnesota · Mississippi · Missouri · Montana · Nebraska · Nevada · New Hampshire · New Jersey · New Mexico · New York · North Carolina · North Dakota · Ohio · Oklahoma · Oregon · Pennsylvania · Rhode Island · South Carolina · South Dakota · Tennessee · Texas · Utah · Vermont · Virginia · Washington · West Virginia · Wisconsin · Wyoming'.split(' · ')

dawg = DAWG.from_list(strings)
clusters = dawg.cluster_by_prefixlen(2)

print('DAWG:')
print(dawg)
print('prefixlen=2 clusters:')
pprint(clusters)
print('clusters serialized as regex-style automata:')
for prefix, suffix_tree in clusters:
    print(prefix + DAWG._serialize(suffix_tree))

print('relaxed serializations:')
for prefix, suffix_tree in clusters:
    # print(type(suffix_tree), suffix_tree)
    dawg = DAWG.from_dawg(suffix_tree)
    relaxer = DAWGRelaxer(dawg)
    rel = sorted(relaxer.relaxable(),
                 key=lambda x: (x[0], repr(x[1])))
    # pprint(rel)
    if rel:
        relaxed = relaxer.relax(rel[0][1])
        # pprint(relaxed)
        print(prefix + DAWG._serialize(relaxed))

# clusters actually work less well for this solution
'''
w = regroup.dawg_weights(d, strings)
# pprint(w, width=1)
pprint(regroup.top_weights(w, 4), width=1)
clusters = regroup.cluster_input(strings)
print(clusters)
'''

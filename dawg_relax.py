
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

dawg = DAWG.from_list(strings)
relaxer = DAWGRelaxer(dawg)
rel = sorted(relaxer.relaxable(), key=lambda x: (x[0], repr(x[1])))
pprint(rel)
relaxed = relaxer.relax(rel[0][1])
pprint(relaxed)
print(dawg.serialize())
print(DAWG.from_dawg(relaxed).serialize())

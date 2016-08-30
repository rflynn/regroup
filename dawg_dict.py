from pprint import pprint
import regroup

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

dictwords = set(w.strip().lower() for w in open('/usr/share/dict/words'))
print('green' in dictwords)
tokenizer = regroup.DictionaryTokenizer(dictwords)
for s in strings:
    tokens = list(tokenizer.tokenize(s.lower()))
    print(s)
    pprint(tokens)
#dawg = regroup.DAWG.from_list(dictwords)
#print(dawg.serialize())

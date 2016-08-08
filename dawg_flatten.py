from pprint import pprint
import regroup
l = [
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
 'JournalP2Black',
 'JournalP2Blue',
 'JournalP2Green']
d = regroup.dawg_make(regroup.trie_make(l))
# pprint(list(regroup.dawg_flatten(d)))
w = regroup.dawg_weights(d, l)
# pprint(w, width=1)
pprint(regroup.top_weights(w, 4), width=1)
clusters = regroup.cluster_input(l)
print(clusters)
clusters.dump()
print(clusters.clusters_by(3))

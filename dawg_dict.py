import regroup

dictwords = [w.strip() for w in open('/usr/share/dict/words')]
dawg = regroup.DAWG.from_list(dictwords)
print(dawg.serialize())

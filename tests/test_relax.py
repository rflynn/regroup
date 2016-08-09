
import unittest

from regroup import DAWG, DAWGRelaxer, suffixes_diff



class TestRelaxer(unittest.TestCase):

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

    def test_relax(self):
        dawg = DAWG.from_list(self.strings)
        serial1 = dawg.serialize()
        self.assertEqual(serial1,
                         '(E(Fgre(en|y)|ntireS[12])|J(27(Green|Red)P[12]|ournalP(1(Bl(ack|ue)|(Green|Red))|2(Bl(ack|ue)|Green))))')
        relaxer = DAWGRelaxer(dawg)
        rel = sorted(relaxer.relaxable(),
                     key=lambda x: (x[0], repr(x[1])))
        # pprint(rel)
        relaxed = relaxer.relax(rel[0][1])
        # pprint(relaxed)
        serial2 = DAWG.from_dawg(relaxed).serialize()
        self.assertEqual(serial2,
                         '(E(Fgre(en|y)|ntireS[12])|J(27(Green|Red)P[12]|ournalP[12](Bl(ack|ue)|(Green|Red))))')


class TestSuffixes(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(0, suffixes_diff({}))

    def test_ue_ack(self):
        self.assertEqual(0, suffixes_diff({'ue': {'': {}},
                                           'ack': {'': {}}}))

    def test_greenp_redp(self):
        self.assertEqual(0,
            suffixes_diff({'GreenP': {'2': {'': {}}, '1': {'': {}}},
                           'RedP': {'2': {'': {}}, '1': {'': {}}}}))

    def test_diff1(self):
        self.assertEqual(1, suffixes_diff({'a': {'diff1': {'': {}}},
                                           'b': {'': {}}}))

    def test_diff2(self):
        self.assertEqual(2, suffixes_diff({'a': {'diff1': {'diff2': {'': {}}}},
                                           'b': {'': {}}}))


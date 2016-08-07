
import re
import unittest
from unittest import skip

from regroup import match, dawg_make


class TestDAWG(unittest.TestCase):

    def test_dawg1(self):
        self.assertEqual(dawg_make({'2': {'3': {'': {}}}}),
                         {'23': {'': {}}})

    def test_dawg1(self):
        self.assertEqual(dawg_make({'1': {'2': {'3': {'': {}}}}}),
                         {'123': {'': {}}})


class TestDigits(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(None, match([]))

    def test_1(self):
        self.assertEqual('0', match(['0']))

    def test_dupes(self):
        self.assertEqual('0', match(['0', '0']))

    def test_01(self):
        self.assertEqual('(00|11)', match(['00', '11']))

    def test_0_1(self):
        self.assertEqual('(0 0|1 1)', match(['0 0', '1 1']))

    def test_float_maybe_dot(self):
        # self.assertEqual('([0-9]|[0-9]\.)', match(['0', '0.']))
        self.assertEqual('0\.?', match(['0', '0.']))

    def test_float_maybe_(self):
        # self.assertEqual('([0-9]|[0-9]\.[0-9])',
        #                match(['0', '0.1']))
        self.assertEqual('0(|.1)',
                         match(['0', '0.1']))

    def test_float_variable_prefix(self):
        self.assertEqual('0(|.12?)',
                         match(['0', '0.1', '0.12']))


    def test_float_variable_prefix23(self):
        # 0(|.1(|23))
        # 0(.1(23)?)?
        self.assertEqual('0(|.1(|23))',
                         match(['0', '0.1', '0.123']))

    def test_numbers(self):
        # (100?|[1-9]|)|[2-9][0-9]?|0
        # (0|(1(|00?|[1-9]))|[2-9][0-9]?)
        # (0|(1(|00?|[1-9]))|[2-9][0-9]?)

        # (100?|[1-9]|)|[02-9][0-9]?
        # (100|[0-9][0-9]?)
        # (1?[0-9][0-9]?)  XXX: too broad
        vals = list(map(str, range(101)))
        pattern = match(vals)
        fullpat = '^({})$'.format(pattern)
        self.assertTrue(all(re.match(fullpat, v) for v in vals))
        self.assertEqual('(0|(1(|00?|[1-9]))|[2-9][0-9]?)', pattern)

    def test_hundreds(self):
        self.assertEqual('[12]00',
                         match(['100', '200']))


class TestStrings(unittest.TestCase):

    '''

    def test_realworld_1(self):
        # ref: http://stackoverflow.com/questions/1410822/how-can-i-detect-common-substrings-in-a-list-of-strings
        self.assertEqual(
            match(['EFgreen',
                   'EFgrey',
                   'EntireS1',
                   'EntireS2',
                   'J27RedP1',
                   'J27GreenP1',
                   'J27RedP2',
                   'J27GreenP2',
                   'JournalP1Black',
                   'JournalP1Blue',
                   'JournalP1Green',
                   #'JournalP1Red',
                   'JournalP2Black',
                   'JournalP2Blue',
                   'JournalP2Green']),
             '(E(Fgre(en|y)|ntireS[12])|J(27(GreenP[12]|RedP[12])|ournalP[12](Bl(ack|ue)|Green)))')
            ['EF(gre(en|y))'
             'EntireS[12]'
             'J27(Red|Green)P[12]'
             'JournalP[12](Red|Green|Blue)'])

    '''



import unittest
from unittest import skip

from regroup import match


class TestDigits(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(None, match([]))

    def test_1(self):
        self.assertEqual('0', match(['0']))

    def test_dupes(self):
        self.assertEqual('0', match(['0', '0']))

    def test_01(self):
        self.assertEqual('[0-9]{2}', match(['00', '11']))

    def test_0_1(self):
        self.assertEqual('[0-9] [0-9]', match(['0 0', '1 1']))

    def test_float_maybe_dot(self):
        self.assertEqual('([0-9]|[0-9]\.)', match(['0', '0.']))

    def test_float_maybe_(self):
        self.assertEqual('([0-9]|[0-9]\.[0-9])',
                         match(['0', '0.1']))

    @skip('')
    def test_numbers(self):
        self.assertEqual('([0-9]|[0-9]{2}|[0-9]{3})',
                         match(list(map(str, range(101)))))

    def test_hundreds(self):
        self.assertEqual('[12]00',
                         match(['100', '200']))

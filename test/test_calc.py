import unittest
from datetime import datetime

from interface import get_vl, get_big_swing


class TestCalc(unittest.TestCase):
    def test_get_vl(self):
        vl = get_vl(2017)
        pass

    def test_get_big_swing(self):
        as_of = datetime(2018, 8, 10).date()
        year_range, swing = get_big_swing(as_of)
        pass


if __name__ == '__main__':
    unittest.main()

import unittest
from datetime import datetime

from back_end.calc import get_vl, get_big_swing, get_swings


class TestCalc(unittest.TestCase):
    def test_get_vl(self):
        vl = get_vl(2017)
        pass

    def test_get_big_swing(self):
        as_of = datetime(2018, 8, 10).date()
        #swing = get_big_swing(as_of)
        swing = get_big_swing()
        pass

if __name__ == '__main__':
    unittest.main()

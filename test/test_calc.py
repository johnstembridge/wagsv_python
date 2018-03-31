import unittest

from calc import get_vl, get_big_swing, get_swings
from models.news import News


class TestCalc(unittest.TestCase):
    def test_get_vl(self):
        vl = get_vl(2017)
        pass

    def test_get_big_swing(self):
        swing = get_big_swing(2018)
        pass

    def test_get_swings(self):
        swings = get_swings(('2017/11/18', '29'))
        pass

if __name__ == '__main__':
    unittest.main()

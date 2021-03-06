import unittest
import datetime
from back_end.interface import front_page_header_file
from back_end.file_access import get_record, get_field, get_fields, file_delimiter, get_records, \
    get_all_records, keys_match, update_html_elements
from back_end.data_utilities import decode_date
from test_data import TestData


class TestInterface(unittest.TestCase):
    maxDiff = None

    def test_get_record(self):
        rec = get_record(TestData.events_file, 'num', '4')
        expected = TestData.example_event_record
        self.assertEqual(rec, expected)

    def test_get_field(self):
        res = get_field(TestData.events_file, 'organiser')
        expected = TestData.example_event_field
        self.assertEqual(res, expected)

    def test_get_fields(self):
        res = get_fields(TestData.events_file, ['num', 'venue'])
        expected = TestData.example_venues_fields
        self.assertEqual(res, expected)

    def test_decode_date(self):
        rec = decode_date('Friday 28 April', 2017)
        expected = datetime.date(2017, 4, 28)
        self.assertEqual(rec, expected)

    def test_file_delimiter(self):
        d = file_delimiter(r'c:\abc\xyz.csv')
        expected = ','
        self.assertEqual(d, expected)
        d = file_delimiter(r'c:\abc\xyz.tab')
        expected = ':'
        self.assertEqual(d, expected)
        d = file_delimiter(r'c:\abc\xyz.txt')
        expected = '\t'
        self.assertEqual(d, expected)

    def test_get_records(self):
        header, recs = get_records(TestData.handicaps_file, 'status', '1')
        self.assertTrue(len(recs) > 0)

    def test_get_records_multi_value(self):
        header, recs = get_records(TestData.handicaps_file, 'player', ['1', '2', '3'])
        self.assertTrue(len(recs) > 0)

    def test_get_file(self):
        head, x = get_all_records(TestData.handicaps_file)
        self.assertTrue(len(x) > 0)

    def test_keys_match_1(self):
        keys = 'num'
        rec1 = {'num': '10', 'type': '1', 'val': 'xxx'}
        rec2 = {'num': '10', 'type': '1', 'val': 'zzz'}
        self.assertTrue(keys_match(rec1, keys, rec2))

    def test_keys_match_2(self):
        keys = ['num']
        rec1 = {'num': '10', 'type': '1', 'val': 'xxx'}
        rec2 = {'num': '10', 'type': '1', 'val': 'zzz'}
        self.assertTrue(keys_match(rec1, keys, rec2))

    def test_keys_match_3(self):
        keys = 'num'
        rec1 = {'num': '10', 'type': '1', 'val': 'xxx'}
        val = '10'
        self.assertTrue(keys_match(rec1, keys, val))

    def test_keys_match_4(self):
        keys = ['num', 'type']
        rec1 = {'num': '10', 'type': '1', 'val': 'xxx'}
        rec2 = {'num': '10', 'type': '1', 'val': 'zzz'}
        self.assertTrue(keys_match(rec1, keys, rec2))

    def test_keys_match_4(self):
        keys = ['num', 'type']
        rec1 = {'num': '10', 'type': '1', 'val': 'xxx'}
        val = ['10', '1']
        self.assertTrue(keys_match(rec1, keys, val))

    def test_update_date(self):
        date = '2018/04/02'
        file = front_page_header_file()
        update_html_elements(file, {'last_updated': date})
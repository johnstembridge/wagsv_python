import copy
import unittest
import datetime
from interface import encode_schedule, decode_schedule, get_event_card
from file_access import get_record, get_field, update_record, file_delimiter, get_records, get_file
from data_utilities import decode_date
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

    def test_update_record_event(self):
        old = get_record(TestData.events_file, 'num', '4')
        new = copy.deepcopy(old)
        new['member_price'] = '25.00'
        new['note'] = '*** New note ***'
        update_record(TestData.events_file, 'num', new)
        rec = get_record(TestData.events_file, 'num', '4')
        expected = new
        self.assertEqual(rec, expected)
        update_record(TestData.events_file, 'num', old)

    def test_update_record_shots(self):
        old = get_event_card('2017', '3', '12')
        new = copy.deepcopy(old)
        new['12'] = '6'
        update_record(TestData.shots_file, ['date', 'course', 'player'], new)
        rec = get_event_card('2017', '3', '12')
        expected = new
        self.assertEqual(rec, expected)
        update_record(TestData.shots_file, ['date', 'course', 'player'], old)

    def test_decode_date(self):
        rec = decode_date('Friday 28 April', 2017)
        expected = datetime.date(2017, 4, 28)
        self.assertEqual(rec, expected)

    def test_decode_schedule(self):
        sched = '10.00 coffee and bacon roles,11.15 tee-off 18 holes,16.00 buffet: lasagne salad desert'
        ss = decode_schedule(sched)
        expected = [
            {'time': datetime.time(10, 0), 'text': 'coffee and bacon roles'},
            {'time': datetime.time(11, 15), 'text': 'tee-off 18 holes'},
            {'time': datetime.time(16, 0), 'text': 'buffet: lasagne salad desert'},
            {'time': datetime.time(0, 0), 'text': None},
            {'time': datetime.time(0, 0), 'text': None},
            {'time': datetime.time(0, 0), 'text': None}
        ]
        self.assertEqual(ss, expected)

    def test_encode_schedule(self):
        sched = [
            {'time': datetime.time(10, 0), 'text': 'coffee and bacon roles'},
            {'time': datetime.time(11, 15), 'text': 'tee-off 18 holes'},
            {'time': datetime.time(16, 0), 'text': 'buffet: lasagne salad desert'},
            {'time': datetime.time(0, 0), 'text': None},
            {'time': datetime.time(0, 0), 'text': None},
            {'time': datetime.time(0, 0), 'text': None}
        ]
        ss = encode_schedule(sched)
        expected = '10.00 coffee and bacon roles,11.15 tee-off 18 holes,16.00 buffet- lasagne salad desert'
        self.assertEqual(ss, expected)

    def test_file_delimiter(self):
        d = file_delimiter(r'c:\abc\xyz.csv')
        expected = ','
        self.assertEqual(d, expected)
        d = file_delimiter(r'c:\abc\xyz.tab')
        expected = ':'
        self.assertEqual(d, expected)

    def test_get_records(self):
        header, recs = get_records(TestData.handicaps_file, 'status', '1')
        self.assertTrue(len(recs) > 0)

    def test_get_records_multi_value(self):
        header, recs = get_records(TestData.handicaps_file, 'player', ['1', '2', '3'])
        self.assertTrue(len(recs) > 0)

    def test_get_file(self):
        head, x = get_file(TestData.handicaps_file)
        self.assertTrue(len(x) > 0)
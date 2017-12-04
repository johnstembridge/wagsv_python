import copy
import unittest
from enumerations import PlayerStatus
import datetime
from interface import get_all_venue_names, get_all_event_names, get_event, save_event, get_record, \
    get_field, encode_schedule, decode_schedule, get_latest_handicaps, get_handicaps, get_players, get_event_scores, \
    get_booked_players, save_event_scores, get_course_data, get_player_handicap, get_event_card
from file_access import get_record, get_field, update_record, file_delimiter, get_records, get_file
from data_utilities import decode_date
from test_data import TestData


class TestInterface(unittest.TestCase):
    maxDiff = None

    def test_get_event_record(self):
        rec = get_record(TestData.events_file, 'num', '4')
        expected = TestData.example_event_record
        self.assertEqual(rec, expected)

    def test_get_course_data_record_1(self):
        rec = get_course_data('4', 2017)
        expected = TestData.example_course_data_1
        self.assertEqual(rec, expected)

    def test_get_course_data_record_2(self):
        rec = get_course_data('4', 1996)
        expected = TestData.example_course_data_2
        self.assertEqual(rec, expected)

    def test_get_course_data_record_3(self):
        rec = get_course_data('21', 2017)
        expected = TestData.example_course_data_3
        self.assertEqual(rec, expected)

    def test_get_event_record_empty(self):
        rec = get_record(TestData.events_file, 'num', '999')
        expected = TestData.example_event_record_empty
        self.assertEqual(rec, expected)

    def test_get_event_field(self):
        res = get_field(TestData.events_file, 'organiser')
        expected = TestData.example_event_field
        self.assertEqual(res, expected)

    def test_get_event(self):
        rec = get_event(2017, '4')
        expected = TestData.example_event
        self.assertDictEqual(rec, expected)

    def test_update_event_record(self):
        old = get_record(TestData.events_file, 'num', '4')
        new = copy.deepcopy(old)
        new['member_price'] = '25.00'
        new['note'] = '*** New note ***'
        update_record(TestData.events_file, 'num', new)
        rec = get_record(TestData.events_file, 'num', '4')
        expected = new
        self.assertEqual(rec, expected)
        update_record(TestData.events_file, 'num', old)

    def test_update_shots_record(self):
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

    def test_get_latest_handicaps(self):
        res = get_latest_handicaps()
        self.assertTrue(len(res) > 0)

    def test_get_handicaps(self):
        res = get_handicaps('2016/08/07')
        self.assertTrue(len(res) > 0)

    def test_get_player_handicap(self):
        res = get_player_handicap('2', '2017/08/07')
        self.assertTrue(res == 20.1)

    def test_get_event_player_card(self):
        card = get_event_card(2017, 3, 3)
        self.assertTrue(len(card) > 0)

    def test_get_event_player_card_none(self):
        card = get_event_card(2017, 3, 2)
        self.assertTrue(len(card) > 0)

    def test_get_file(self):
        head, x = get_file(TestData.handicaps_file)
        self.assertTrue(len(x) > 0)

    def test_get_members(self):
        res = get_players('2016/08/07', 1)
        self.assertTrue(len(res) > 0)

    def test_get_players(self):
        res = get_players('2016/08/07', [PlayerStatus.member, PlayerStatus.guest])
        self.assertTrue(len(res) > 0)

    def test_get_ex_members(self):
        res = get_players('2016/08/07', PlayerStatus.ex_member)
        self.assertTrue(len(res) > 0)

    def test_get_event_scores(self):
        rec = get_event_scores(2016, '1')
        self.assertTrue(len(rec) > 0)

    def test_get_booked_players(self):
        res = get_booked_players('2017', 3)
        self.assertTrue(len(res) > 0)

    def test_save_event_scores(self):
        year = '2017'
        event_id = 3
        fields = ['player', 'points', 'strokes', 'handicap', 'status']
        data = [['3', 38, '92', '21.8', 0],
                ['222', 34, '88', '14.3', 0],
                ['28', 32, '92', '16', 0],
                ['384', 31, '93', '16', 0],
                ['93', 29, '96', '16.3', 0],
                ['160', 29, '91', '11.8', 0],
                ['260', 29, '103', '23.1', 0],
                ['225', 29, '92', '12.4', 0],
                ['316', 28, '89', '8.1', 0],
                ['162', 28, '104', '23.5', 0],
                ['294', 28, '92', '11.9', 0],
                ['290', 28, '104', '24', 1],
                ['129', 27, '94', '12.5', 0],
                ['178', 23, '103', '18.1', 0],
                ['24', 20, '116', '28', 0],
                ['12', 16, '121', '28', 0]]

        save_event_scores(year, event_id, fields, data)

import unittest
from enumerations import PlayerStatus
from interface import get_event, get_latest_handicaps, get_handicaps, get_players, get_event_scores, \
    get_booked_players, save_event_scores, get_course_data, get_player_handicap, get_event_card, get_venue_by_name
from file_access import get_record
from test_data import TestData


class TestInterface(unittest.TestCase):
    maxDiff = None

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

    def test_get_event(self):
        rec = get_event(2017, '4')
        expected = TestData.example_event
        self.assertDictEqual(rec, expected)

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

    def test_get_venue_by_name(self):
        rec = get_venue_by_name('Gatton Manor')
        expected = TestData.example_venue
        self.assertDictEqual(rec, expected)

import unittest
import datetime

from back_end.file_access import get_record
from globals.enumerations import PlayerStatus
from back_end.interface import *
from back_end.table import Table
from test_data import TestData


class TestInterface(unittest.TestCase):
    maxDiff = None

    def test_get_vl_scores(self):
        scores = get_scores(2016, PlayerStatus.member)
        pass

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

    def test_get_event_shots(self):
        res = get_event_cards(348)
        expected = TestData.example_event_cards
        self.assertEqual(res, expected)

    def test_get_event_result_by_year_and_name(self):
        res = get_results_by_year_and_name(2017, 'Mill Ride')
        expected = TestData.example_event_result
        self.assertEqual(res, expected)

    def test_get_event(self):
        rec = get_event(2017, '4')
        expected = TestData.example_event
        self.assertDictEqual(rec, expected)

    def test_get_handicaps(self):
        res = get_handicaps('2016/08/07')
        self.assertTrue(len(res) > 0)

    def test_get_player_handicap(self):
        res = get_player_handicap('2', '2017/08/07')
        self.assertTrue(res == 20.1)

    def test_get_player_name(self):
        res = get_player_name('2')
        self.assertTrue(res == 'Peter Berring')

    def test_get_player_names(self):
        res = get_player_names(['1', '2'])
        self.assertTrue(res == ['Fred Berring', 'Peter Berring'])

    def test_get_event_player_card(self):
        card = get_event_card(2017, 3, 3)
        self.assertTrue(len(card) > 0)

    def test_get_event_player_card_none(self):
        card = get_event_card(2017, 3, 2)
        self.assertTrue(len(card) > 0)

    def test_get_members(self):
        res = get_players('2018/01/01', 1)
        self.assertTrue(len(res) > 0)

    def test_get_members(self):
        res = get_current_members()
        self.assertTrue(len(res) > 0)

    def test_get_member(self):
        res = get_member('home_email', 'john.stembridge@gmail.com')
        self.assertEqual('john.stembridge@gmail.com', res['home_email'])

    def test_get_players(self):
        res = get_players('2016/08/07', [PlayerStatus.member, PlayerStatus.guest])
        self.assertTrue(len(res) > 0)

    def test_get_ex_members(self):
        res = get_players('2016/08/07', PlayerStatus.ex_member)
        self.assertTrue(len(res) > 0)

    def test_get_event_scores(self):
        tab = get_event_scores(328)
        self.assertTrue(len(tab.data) > 0)

    def test_get_booked_players(self):
        res = get_booked_players(2017, 3)
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

        save_event_scores(year, event_id, Table(fields, data))

    def test_get_venue_by_name(self):
        rec = get_venue(4)
        expected = TestData.example_venue
        self.assertDictEqual(rec, expected)

    def test_get_tour_events(self):
        rec = get_tour_events(2017, 5, 6)
        expected = TestData.example_tour_events
        self.assertEqual(rec, expected)

    def test_get_tour_event_list_from_scores(self):
        res = get_tour_event_list_from_scores(2016, 3)
        self.assertTrue(len(res) > 0)

    def test_get_tour_scores(self):
        res = get_tour_scores(2017, 5)
        self.assertTrue(len(res) > 0)

    def test_get_last_event(self):
        last = get_last_event()

    # def test_calc_event_result(self):
    #     year = '2017'
    #     event_id = '3'
    #     data = TestData.event_result_return
    #     result = calc_event_positions(year, event_id, data)
    #     expected = TestData.event_result_sorted
    #     self.assertEqual(result, expected)

    def test_get_member_select_list(self):
        res = get_member_select_choices()

    def test_get_events_since(self):
        date_range = [datetime.date(2016, 1, 1), datetime.date(2017, 12, 31)]
        res = get_events_in(date_range)
        pass

    def test_get_trophy(self):
        rec = get_trophy('3')
        self.assertTrue(rec['sponsor'] == 'Mike Dearden')

    def test_get_course(self):
        course = get_course(29)
        self.assertEqual(course['name'], 'Pine Ridge')

    def test_get_event_for_date(self):
        event = get_event(date='2001/10/20')
        self.assertEqual(event['course'], 'Pine Ridge')


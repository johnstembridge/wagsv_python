import unittest
import datetime

from back_end.file_access import get_record
from globals.enumerations import PlayerStatus
from back_end.interface import *
from back_end.table import Table
from test_data import TestData


from flask import Flask
from globals.app_setup import init_app


class TestInterface(unittest.TestCase):
    maxDiff = None
    app = Flask(__name__)
    init_app(app, multi_thread=False)

    def test_update_event_winners(self):
        with self.app.app_context():
            for event in get_all_events():
                if not event.average_score:
                    scores = get_event_scores(event.id)
                    if len(scores.data) > 0:
                        print(event)
                        update_event_winner(event, scores)
                        db_session.commit()

    def test_get_vl_scores(self):
        with self.app.app_context():
            scores = get_scores(2016, PlayerStatus.member)
            pass

    # def test_get_course_data_record_1(self):
    #     with self.app.app_context():
    #         rec = get_course_data('4', 2017)
    #         expected = TestData.example_course_data_1
    #         self.assertEqual(rec, expected)
    #
    # def test_get_course_data_record_2(self):
    #     with self.app.app_context():
    #         rec = get_course_data('4', 1996)
    #         expected = TestData.example_course_data_2
    #         self.assertEqual(rec, expected)
    #
    # def test_get_course_data_record_3(self):
    #     with self.app.app_context():
    #         rec = get_course_data('21', 2017)
    #         expected = TestData.example_course_data_3
    #         self.assertEqual(rec, expected)
    #
    # def test_get_event_record_empty(self):
    #     with self.app.app_context():
    #         rec = get_record(TestData.events_file, 'num', '999')
    #         expected = TestData.example_event_record_empty
    #         self.assertEqual(rec, expected)
    #
    # def test_get_event_shots(self):
    #     with self.app.app_context():
    #         res = get_event_cards(348)
    #         expected = TestData.example_event_cards
    #         self.assertEqual(res, expected)
    #
    # def test_get_event(self):
    #     with self.app.app_context():
    #         rec = get_event(2017, '4')
    #         expected = TestData.example_event
    #         self.assertDictEqual(rec, expected)
    #
    # def test_get_player_names(self):
    #     with self.app.app_context():
    #         res = get_player_names(['1', '2'])
    #         self.assertTrue(res == ['Fred Berring', 'Peter Berring'])
    #
    # def test_get_event_player_card(self):
    #     with self.app.app_context():
    #         card = get_event_card(2017, 3, 3)
    #         self.assertTrue(len(card) > 0)
    #
    # def test_get_event_player_card_none(self):
    #     with self.app.app_context():
    #         card = get_event_card(2017, 3, 2)
    #         self.assertTrue(len(card) > 0)
    #
    # def test_get_member(self):
    #     with self.app.app_context():
    #         res = get_member('home_email', 'john.stembridge@gmail.com')
    #         self.assertEqual('john.stembridge@gmail.com', res['home_email'])

    def test_get_event_scores(self):
        with self.app.app_context():
            tab = get_event_scores(328)
            self.assertTrue(len(tab.data) > 0)

    # def test_get_venue_by_name(self):
    #     with self.app.app_context():
    #         rec = get_venue(4)
    #         expected = TestData.example_venue
    #         self.assertDictEqual(rec, expected)
    #
    # def test_get_tour_scores(self):
    #     with self.app.app_context():
    #         res = get_tour_scores(2017, 5)
    #         self.assertTrue(len(res) > 0)

    def test_get_last_event(self):
        with self.app.app_context():
            last = get_latest_event()

    def test_get_member_select_list(self):
        with self.app.app_context():
            res = get_member_select_choices()

    def test_get_events_since(self):
        with self.app.app_context():
            date_range = [datetime.date(2016, 1, 1), datetime.date(2017, 12, 31)]
            res = get_events_in(date_range)
            pass

    # def test_get_trophy(self):
    #     with self.app.app_context():
    #         rec = get_trophy('3')
    #         self.assertTrue(rec['sponsor'] == 'Mike Dearden')
    #
    def test_get_course(self):
        with self.app.app_context():
            course = get_course(29)
            self.assertEqual(course.name, 'Pine Ridge')

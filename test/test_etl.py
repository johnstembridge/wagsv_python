import os
import unittest
from back_end.file_access import get_all_records, get_records
from back_end.table import Table
from test_data import TestData
from back_end.interface import get_member_by_name, get_booking, save_booking, get_player_by_name, get_event, save_event_result
from models.wags_db import Guest
from back_end.data_utilities import first_or_default, parse_float, parse_date
from globals.enumerations import PlayerStatus


class TestEtl(unittest.TestCase):
    maxDiff = None

    # def test_etl_bookings(self):
    #     year = '2018'
    #     event = 'event14.csv'
    #     event_id = 381
    #     booking_file = os.path.join(TestData.data_location, year, event)
    #     old = Table(*get_all_records(booking_file))
    #     for old_booking in old.rows():
    #         member_name = old_booking['name']
    #         member = get_member_by_name(member_name)
    #         booking = get_booking(event_id, member.id)
    #         booking.date = parse_date(old_booking['date'], reverse=True)
    #         booking.playing = old_booking['playing'] == '1'
    #         booking.comment = old_booking['comment']
    #         number = int(old_booking['number'])
    #         guests = []
    #         for count in range(1, number):
    #             name = old_booking['guest{}'.format(count)]
    #             hcap = parse_float(old_booking['guest{}_hcap'.format(count)])
    #             guest = first_or_default([g for g in booking.guests if g.name == name], Guest(name=name, booking=booking))
    #             known_player = get_player_by_name(name)
    #             if known_player:
    #                 state = known_player.state_as_of(booking.date)
    #                 if state.status == PlayerStatus.member:
    #                     hcap = state.handicap
    #             guest.handicap = hcap
    #             guests.append(guest)
    #         booking.guests = guests
    #         save_booking(booking, True)
    #     self.assertEqual(1, 1)

    def test_etl_results(self):
        date = '2018/07/27'
        event_id = 373
        scores_file = os.path.join(TestData.data_location, 'scores.tab')
        shots_file = os.path.join(TestData.data_location, 'shots.tab')
        oldscores = Table(*get_records(scores_file, 'date', date))
        oldshots = Table(*get_records(shots_file, 'date', date))
        holes = [str(h) for h in range(1, 19)]
        oldshots.coerce_columns(['player'] + holes, int)
        oldscores.coerce_columns(['player', 'position', 'points', 'strokes', 'status'], int)
        oldscores.sort('player')
        oldshots.sort('player')
        oldscores.add_column('card', [s for s in oldshots.get_columns(holes)])
        oldscores.coerce_column('status', PlayerStatus)
        oldscores.rename_column('player', 'player_id')
        oldscores.rename_column('strokes', 'shots')
        oldscores.sort('position')
        save_event_result(event_id, oldscores)

        self.assertEqual(1, 1)

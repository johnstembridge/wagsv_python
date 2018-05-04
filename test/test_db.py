import unittest

from models.wags_db import Event, Venue, Player
from globals.db_setup import db_session


class TestDb(unittest.TestCase):

    def test_venue(self):
        ve = Venue.query.get(19)
        pass
        #db_session.commit()

    def test_player(self):
        pl = Player.query.get(12)
        pass
        #db_session.commit()

    def test_event(self):
        ev = Event.query.get(364)
        pass
        #ev.max = 50
        #db_session.commit()

    def test_missing(self):
        ev = Event.query.get(999)
        self.assertEqual(ev, None)


if __name__ == '__main__':
    unittest.main()

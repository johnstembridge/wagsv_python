import unittest

from models.wags_db import Event, Venue, Player, Member, Handicap, EnumType, db
from globals.db_setup import db_session
from sqlalchemy import text


class TestDb(unittest.TestCase):

    # def setUp(self):
    #     pass
    #
    # def test_venue(self):
    #     #ve = Venue.query.get(19)
    #     ve = db_session.query(Venue).get(19)
    #     pass
    #     # db_session.commit()
    #
    # def test_player(self):
    #     #pl = Player.query.get(12)
    #     pl =  db_session.query(Player).get(12)
    #     pass
    #     # db_session.commit()
    #
    # def test_handicaps(self):
    #     me = Handicap.query.filter_by(player_id=12).all()
    #     pass
    #
    # def test_update_event(self):
    #     #ev = Event.query.filter_by(id=364).first()
    #     ev = db_session.query(Event).get(364)
    #     ev.max = 28
    #     db_session.commit()
    #     pass
    #
    # def test_get_event(self):
    #     ev = Event.query.filter_by(id=364).first()
    #     pass
    #   for i in range(382):
    #         ev = db_session.query(Event).get(i)
    #         pass
    #
    def test_get_events_for_year(self):
        year = 2018
        stmt = text("select id from events where strftime('%Y', date)=:year order by date").params(year=year)
        evs = db_session.query(Event).from_statement(stmt).all()
        pass
    #
    # def test_missing(self):
    #     ev = db_session.query(Event).get(999)
    #     self.assertEqual(ev, None)


if __name__ == '__main__':
    unittest.main()

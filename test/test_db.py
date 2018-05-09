import unittest

from models.wags_db import Event, Venue, Player, TestEnum
from globals.db_setup import db_session
from sqlalchemy import text
from globals.enumerations import EventType


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
    def test_update_event(self):
        #ev = Event.query.filter_by(id=364).first()
        ev = db_session.query(Event).get(364)
        ev.max = 28
        db_session.commit()
        pass

    # def test_get_event(self):
    #     #ev = Event.query.filter_by(id=364).first()
    #     for i in range(382):
    #         ev = db_session.query(Event).get(i)
    #         pass
    #
    # def test_get_events_for_year(self):
    #     year = "2018"
    #     ev = db_session.query(Event).from_statement(
    #         text("select * from events where strftime('%Y', date)=:year")).params(year=year).all()
    #     pass
    #
    # def test_missing(self):
    #     ev = db_session.query(Event).get(999)
    #     self.assertEqual(ev, None)
    #
    # def test_test_enum(self):
    #     #te = TestEnum.query.get(1)
    #     te = db_session.query(TestEnum).all()
    #     te.type = EventType.wags_vl_event
    #     db_session.commit()


if __name__ == '__main__':
    unittest.main()

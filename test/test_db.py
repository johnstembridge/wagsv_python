import unittest

from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker

from models.wags_db import Base, Event, Venue, Player, Member, Handicap, EnumType, CourseData
from globals import config


class TestDb(unittest.TestCase):

    def setUp(self):
        db_path = config.get('db_path')
        self.engine = create_engine(db_path, echo=True)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

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
        #evs = get_event_list(year)
        stmt = text("select id from events where strftime('%Y', date)=:year order by date").params(year=str(year))
        evs = self.session.query(Event).from_statement(stmt).all()
        pass

    def test_get_card_for_course(self):
        year = 2018
        id = 102
        stmt = text("select * from course_data where course_id=:id and year>=:year order by year")
        res = self.session.query(CourseData).from_statement(stmt).params(id=str(id), year=str(year)).first()

        pass
    #
    # def test_missing(self):
    #     ev = db_session.query(Event).get(999)
    #     self.assertEqual(ev, None)


if __name__ == '__main__':
    unittest.main()

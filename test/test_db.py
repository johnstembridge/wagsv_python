import unittest

from back_end.db_setup import db_session
from models.wags_db import Event


class TestDb(unittest.TestCase):

    def test_update(self):
        ev = Event.query.get(3)
        ev.max = 50
        db_session.commit()

    def test_missing(self):
        ev = Event.query.get(99)
        self.assertEqual(ev, None)


if __name__ == '__main__':
    unittest.main()

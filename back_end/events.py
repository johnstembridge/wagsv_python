import datetime


class Event:

    def __init__(self, event_id):
        self.event_id = event_id
        self.name = None
        self.organiser = None
        self.venue = None
        self.date = datetime.date.today()
        self.member_price = 0.0
        self.guest_price = 0.0
        self.start_booking = datetime.date.today()
        self.end_booking = datetime.date.today()
        self.max = 0
        self.notes = None
        self.schedule = []

    def as_json(self):
        data = {'event_id': self.event_id,
                'name': self.name,
                'date': self.date,
                'venue': self.venue,
                'organiser': self.organiser,
                'member_price': self.member_price,
                'guest_price': self.guest_price,
                'start_booking': self.start_booking,
                'end_booking': self.end_booking,
                'max': self.max,
                'notes': self.notes,
                'schedule': [si.as_json() for si in self.schedule]
                }
        return data

    def add_schedule_item(self, item):
        self.schedule.append(item)

    def get_all_event_names():
        return ['Stembridge Sandwedge']

    def get_all_venue_names():
        return ['Chartham Park']


class ScheduleItem:
    def __init__(self, time=None, text=None):
        self.time = time
        self.text = text

    def as_json(self):
        data = {
            'time': self.time,
            'text': self.text
        }
        return data

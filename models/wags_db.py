from wags_user import db
from globals.enumerations import EventType, PlayerStatus, MemberStatus
import sqlalchemy.types as types
from globals import config


class EnumType(types.TypeDecorator):
    impl = types.SmallInteger

    def __init__(self, data, **kw):
        self.data = data
        super(EnumType, self).__init__(**kw)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return value.value

    def process_result_value(self, value, dialect):
        return self.data(value)


class IntArray(types.TypeDecorator):
    impl = types.String

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = ','.join([str(x) for x in value])
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = [int(x) for x in value.split(',')]
        return value


class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    type = db.Column(EnumType(EventType), nullable=False)
    member_price = db.Column(db.Numeric(precision=5, scale=2))
    guest_price = db.Column(db.Numeric(precision=5, scale=2))
    note = db.Column(db.String(250))
    booking_start = db.Column(db.Date)
    booking_end = db.Column(db.Date)
    max = db.Column(db.Integer)

    scores = db.relationship('Score', back_populates='event')

    organiser_id = db.Column(db.Integer, db.ForeignKey("members.id"))
    organiser = db.relationship('Member', back_populates="events_organised")

    trophy_id = db.Column(db.Integer, db.ForeignKey("trophies.id"))
    trophy = db.relationship('Trophy', back_populates='events')

    venue_id = db.Column(db.Integer, db.ForeignKey("venues.id"))
    venue = db.relationship('Venue', back_populates='events')

    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"))
    course = db.relationship('Course', back_populates='events')

    schedule = db.relationship('Schedule', back_populates='event')

    tour_event_id = db.Column(db.Integer, db.ForeignKey("events.id"))
    tour_events = db.relationship('Event', backref=db.backref("tour_event", remote_side=id))

    winner_id = db.Column(db.Integer, db.ForeignKey("players.id"))
    winner = db.relationship('Player', back_populates="events_won")

    average_score = db.Column(db.Numeric(precision=3, scale=1))

    def __repr__(self):
        if self.type == EventType.wags_vl_event:
            return '<Event: {} {}>'.format(self.course.name, self.date)
        elif self.type == EventType.wags_tour:
            return '<Tour: {} {}>'.format(self.venue.name, self.date)
        else:
            return '<Non-Event: {} {}>'.format(self.venue.name, self.date)


class Trophy(db.Model):
    __tablename__ = "trophies"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    events = db.relationship("Event", order_by=Event.id, back_populates="trophy")

    def url(self):
        return config.url_for_user('trophy', trophy=self.id)

    def __repr__(self):
        return '<Trophy: {}>'.format(self.name)


class Venue(db.Model):
    __tablename__ = "venues"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    directions = db.Column(db.String(500))
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.id"))
    contact = db.relationship("Contact", uselist=False, back_populates="venue")
    events = db.relationship("Event", order_by=Event.id, back_populates="venue")
    courses = db.relationship("Course", back_populates="venue")

    def __repr__(self):
        return '<Venue: {}>'.format(self.name)


class Course(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("venues.id"))
    name = db.Column(db.String(100), nullable=False)
    events = db.relationship("Event", order_by=Event.id, back_populates="course")
    venue = db.relationship('Venue', back_populates="courses")
    cards = db.relationship('CourseData', back_populates="course")

    def __repr__(self):
        return '<Course: {}>'.format(self.name)


class CourseData(db.Model):
    __tablename__ = "course_data"
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), primary_key=True)
    year = db.Column(db.Integer, primary_key=True)
    sss = db.Column(db.Integer)
    si = db.Column(IntArray(60), nullable=False)
    par = db.Column(IntArray(60), nullable=False)
    course = db.relationship("Course", back_populates="cards")

    def __repr__(self):
        return '<Course Data: {} {}>'.format(self.course.name, self.year)


class Schedule(db.Model):
    __tablename__ = "schedules"
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), primary_key=True)
    time = db.Column(db.Time, primary_key=True)
    text = db.Column(db.String(100), nullable=False)
    event = db.relationship("Event", back_populates="schedule")

    def __repr__(self):
        return '<Schedule: {} {}>'.format(self.event, self.time)


class Contact(db.Model):
    __tablename__ = "contacts"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    address = db.Column(db.String(120))
    post_code = db.Column(db.String(12))
    phone = db.Column(db.String(20))
    url = db.Column(db.String(120))
    venue = db.relationship("Venue", uselist=False, back_populates="contact")
    member = db.relationship("Member", uselist=False, back_populates="contact")

    def __repr__(self):
        return '<Contact: {}>'.format(self.id)


class Player(db.Model):
    __tablename__ = "players"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(25), nullable=False)
    last_name = db.Column(db.String(25), nullable=False)
    member = db.relationship('Member', uselist=False, back_populates="player")
    events_won = db.relationship("Event",  back_populates="winner")
    scores = db.relationship("Score",  back_populates="player")
    handicaps = db.relationship("Handicap",  back_populates="player")

    def full_name(self):
        return self.first_name + ' ' + self.last_name

    def __repr__(self):
        return '<Player: {}>'.format(self.full_name())


class Member(db.Model):
    __tablename__ = "members"
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), nullable=False)
    contact = db.relationship('Contact', uselist=False, back_populates="member")
    status = db.Column(EnumType(MemberStatus), nullable=False)
    accepted = db.Column(db.Date)
    resigned = db.Column(db.Date)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    player = db.relationship("Player", back_populates="member")
    proposer_id = db.Column(db.Integer, db.ForeignKey("members.id"), nullable=False)
    proposed = db.relationship("Member", backref=db.backref("proposer", remote_side=id))
    events_organised = db.relationship("Event",  back_populates="organiser")

    def __repr__(self):
        return '<Member: {}>'.format(self.player.full_name())


class Handicap(db.Model):
    __tablename__ = "handicaps"
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"), primary_key=True)
    date = db.Column(db.Date, primary_key=True)
    status = db.Column(EnumType(PlayerStatus), nullable=False)
    handicap = db.Column(db.Numeric(precision=3, scale=1))
    player = db.relationship("Player", back_populates="handicaps")

    def __repr__(self):
        return '<Handicap - Player: {}, Date: {}>'.format(self.player.full_name(), self.date)


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    shots = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, nullable=False)
    card = db.Column(IntArray(60))
    player = db.relationship("Player", back_populates="scores")
    event = db.relationship("Event", back_populates="scores")

    def __repr__(self):
        return '<Score - Event: {}, Player: {}>'.format(self.event, self.player.full_name())


db.create_all()


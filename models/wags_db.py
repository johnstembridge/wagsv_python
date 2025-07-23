from flask_login import UserMixin
from globals.app_setup import db
from globals import config
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

from back_end.data_utilities import fmt_date, in_date_range, extract_substrings, first_or_default
from back_end.calc import calc_playing_handicap_for_event
from globals.enumerations import EventType, EventBooking, PlayerStatus, MemberStatus, UserRole, Function

import datetime
from time import time, localtime, strftime

Base = db.Model
Column = db.Column
Integer = db.Integer
SmallInteger = db.SmallInteger
Date = db.Date
Time = db.Time
Numeric = db.Numeric
String = db.String
ForeignKey = db.ForeignKey
Boolean = db.Boolean
relationship = db.relationship
backref = db.backref


class EnumType(db.TypeDecorator):
    impl = SmallInteger

    def __init__(self, data, **kw):
        self.data = data
        super(EnumType, self).__init__(**kw)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return value.value

    def process_result_value(self, value, dialect):
        return self.data(value)


class IntArray(db.TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = ','.join([str(x) for x in value])
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = [int(x) for x in value.split(',')]
        return value


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    type = Column(EnumType(EventType), nullable=False)
    member_price = Column(Numeric(precision=5, scale=2))
    guest_price = Column(Numeric(precision=5, scale=2))
    note = Column(String(250))
    booking_start = Column(Date)
    booking_end = Column(Date)
    max = Column(Integer)
    max_guests = Column(Integer, nullable=False)

    scores = relationship('Score', order_by="Score.position", back_populates='event')

    organiser_id = Column(Integer, ForeignKey("members.id"))
    organiser = relationship('Member', back_populates="events_organised")

    trophy_id = Column(Integer, ForeignKey("trophies.id"))
    trophy = relationship('Trophy', back_populates='events')

    venue_id = Column(Integer, ForeignKey("venues.id"))
    venue = relationship('Venue', back_populates='events')

    course_id = Column(Integer, ForeignKey("courses.id"))
    course = relationship('Course', back_populates='events')

    schedule = relationship('Schedule', back_populates='event', cascade="all, delete, delete-orphan")

    tour_event_id = Column(Integer, ForeignKey("events.id"))
    tour_events = relationship('Event', order_by=date, backref=backref("tour_event", remote_side=id))

    winner_id = Column(Integer, ForeignKey("players.id"))
    winner = relationship('Player', back_populates="events_won")

    bookings = relationship("Booking", back_populates="event")

    average_score = Column(Numeric(precision=3, scale=1))

    def full_name(self):
        name = ''
        if self.trophy:
            name += self.trophy.name + ' '
        name += self.venue.name + ' ' + fmt_date(self.date)
        return name

    def is_editable(self):
        override = config.get('override')
        return override or self.date.year >= datetime.date.today().year

    def is_booking_editable(self):
        override = config.get('override')
        tour_event = self.tour_event_id
        today = datetime.date.today()
        return override or (today <= self.date) and not tour_event

    def is_result_editable(self):
        override = config.get('override')
        today = datetime.date.today()
        return override or (today >= self.date) and (today.year == self.date.year)

    def are_tour_bookings_editable(self):
        return self.type == EventType.wags_tour

    def is_bookable(self):
        return self.bookable() == EventBooking.open

    def is_viewable(self):
        return self.bookable() == EventBooking.viewable

    def bookable(self):
        # result:  see EventBooking enum
        if config.get('override'):
            return EventBooking.open
        if self.type == EventType.cancelled:
            return EventBooking.cancelled
        if self.type in [EventType.non_event, EventType.minotaur, EventType.wags_tour] or self.tour_event_id:
            return EventBooking.not_applicable
        if self.booking_start:
            booking_start = self.booking_start
            booking_end = self.booking_end
            in_range = in_date_range(datetime.date.today(), booking_start, booking_end)
        else:
            in_range = False
        return EventBooking.open if in_range and not self.at_capacity() else EventBooking.viewable

    def total_playing(self):
        return sum([(1 + len(m.guests)) for m in self.bookings if m.playing])

    def at_capacity(self):
        return self.max and self.max > 0 and self.total_playing() >= self.max

    def has_reserve_list(self):
        return self.id in config.get('event_has_reserve_list')

    def completed(self):
        return self.winner != None # scoring event and scores entered

    def __repr__(self):
        if self.type == EventType.wags_vl_event:
            return '<Event: {} {}>'.format(self.course.name, self.date)
        elif self.type == EventType.wags_tour:
            return '<Tour: {} {}>'.format(self.venue.name, self.date)
        elif self.type == EventType.minotaur:
            return '<Tour: {} {}>'.format(self.venue.name, self.date)
        else:
            return '<Non-Event: {} {}>'.format(self.venue.name, self.date)


class Trophy(Base):
    __tablename__ = "trophies"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    events = relationship("Event", order_by="desc(Event.date)", back_populates="trophy")

    def __repr__(self):
        return '<Trophy: {}>'.format(self.name)


class Venue(Base):
    __tablename__ = "venues"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    directions = Column(String(500))
    contact_id = Column(Integer, ForeignKey("contacts.id"))
    contact = relationship("Contact", uselist=False, back_populates="venue")
    events = relationship("Event", order_by=Event.id, back_populates="venue")
    courses = relationship("Course", back_populates="venue")

    def __repr__(self):
        return '<Venue: {}>'.format(self.name)


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    venue_id = Column(Integer, ForeignKey("venues.id"))
    name = Column(String(100), nullable=False)
    events = relationship("Event", order_by=Event.id, back_populates="course")
    venue = relationship('Venue', back_populates="courses")
    cards = relationship('CourseData', order_by="CourseData.year", back_populates="course")

    def course_data_as_of(self, year):
        data = [cd for cd in self.cards if cd.year >= year]
        if len(data) > 0:
            return data[0]
        else:
            return None

    def full_name(self):
        course = self.name
        if '(' in course:
            course = first_or_default(extract_substrings(course, '()'), course)
        if self.venue and course != self.venue.name:
            return '{} ({})'.format (self.venue.name, course)
        else:
            return self.name

    def __repr__(self):
        return '<Course: {}>'.format(self.name)


class CourseData(Base):
    __tablename__ = "course_data"
    course_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)
    year = Column(Integer, primary_key=True)
    sss = Column(Integer)
    si = Column(IntArray(60), nullable=False)
    par = Column(IntArray(60), nullable=False)
    course = relationship("Course", back_populates="cards")
    rating = Column(Numeric(precision=3, scale=1))
    slope = Column(Integer)

    def course_par(self):
        return sum(self.par)

    def __repr__(self):
        return '<Course Data: {} {}>'.format(self.course.name, self.year)


class Schedule(Base):
    __tablename__ = "schedules"
    event_id = Column(Integer, ForeignKey("events.id"), primary_key=True)
    time = Column(Time, primary_key=True)
    text = Column(String(100), nullable=False)
    event = relationship("Event", back_populates="schedule")

    def __lt__(self, other):  # for sorting
        return self.time < other.time

    def __repr__(self):
        return '<Schedule: {} {}>'.format(self.event, self.time)


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    email = Column(String(120))
    address = Column(String(120))
    post_code = Column(String(12))
    phone = Column(String(20))
    url = Column(String(120))
    venue = relationship("Venue", uselist=False, back_populates="contact")
    member = relationship("Member", uselist=False, back_populates="contact")

    def __repr__(self):
        return '<Contact: {}>'.format(self.id)


class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(25), nullable=False)
    last_name = Column(String(25), nullable=False)
    member = relationship('Member', uselist=False, back_populates="player")
    events_won = relationship("Event", back_populates="winner")
    scores = relationship("Score", back_populates="player")
    handicaps = relationship("Handicap", order_by="Handicap.date", back_populates="player")

    def full_name(self):
        return self.first_name + ' ' + self.last_name

    def state_as_of(self, date):
        state = [h for h in self.handicaps if h.date <= date]
        state.sort(key=lambda s: s.date)
        if len(state) > 0:
            state = state[-1]
            if self.member:
                if state.status.current_member() and date < self.member.qualifying_date():
                    state.status = PlayerStatus.non_vl
                    events_played = [s for s in self.scores if
                            s.event.type == EventType.wags_vl_event and
                            s.event.date >= self.member.accepted and
                            s.event.date <= date]
                    first_year = datetime.date(*config.get('start_date')).year
                    if len(events_played) <= 3 and date.year > first_year:
                        state.status = PlayerStatus.new # member must have played at least 3 events to qualify for VL
                elif state.status in [PlayerStatus.new, PlayerStatus.non_vl] and date >= self.member.qualifying_date():
                    state.status = PlayerStatus.member
            return state
        else:
            status = PlayerStatus.ex_member if self.member else PlayerStatus.guest
            return Handicap(player_id=self.id, status=status, handicap=0, date=date)

    def states_up_to(self, date):
        state = [self.state_as_of(h.date) for h in self.handicaps if h.date <= date]
        state.sort(key=lambda s: s.date)
        if len(state) > 0:
            return sorted(state, key=lambda s: s.date, reverse=True)
        else:
            return [Handicap(player_id=self.id, status=PlayerStatus.guest, handicap=0, date=date.today())]

    def score_for(self, event_id):
        scores = [s for s in self.scores if s.event_id == event_id]
        if len(scores) > 0:
            return scores[0]
        else:
            return Score(event_id=event_id, points=0, shots=0, position=0, player=self)

    def __repr__(self):
        return '<Player: {}>'.format(self.full_name())


class Member(Base):
    __tablename__ = "members"
    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=False)
    contact = relationship('Contact', uselist=False, back_populates="member")
    status = Column(EnumType(MemberStatus), nullable=False)
    accepted = Column(Date)
    resigned = Column(Date)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    player = relationship("Player", back_populates="member")
    proposer_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    club_membership = Column(String(100))
    proposed = relationship("Member", backref=backref("proposer", remote_side=id))
    events_organised = relationship("Event", back_populates="organiser")
    bookings = relationship("Booking", back_populates="member")
    user = relationship('User', uselist=False, back_populates="member")
    committee = relationship("Committee", back_populates="member")

    def accepted_date(self):
        return self.accepted or datetime.date(*config.get('start_date'))


    def qualifying_date(self):
        start_date = datetime.date(*config.get('start_date'))
        if self.accepted and self.accepted.year > start_date.year:
            return self.accepted.replace(year=self.accepted.year + 1)
        else:
            return start_date

    def __repr__(self):
        return '<Member: {}>'.format(self.player.full_name())


class Committee(Base):
    __tablename__ = "committee"
    member_id = Column(Integer, ForeignKey('members.id'), nullable=False, primary_key=True)
    function = Column(EnumType(Function), nullable=False, primary_key=True)
    member = relationship("Member", back_populates="committee")

    def __repr__(self):
        return '<Committee {} {}>'.format(self.function.name, self.member.player.full_name())


class Handicap(Base):
    __tablename__ = "handicaps"
    player_id = Column(Integer, ForeignKey("players.id"), primary_key=True)
    date = Column(Date, primary_key=True)
    status = Column(EnumType(PlayerStatus), nullable=False)
    handicap = Column(Numeric(precision=3, scale=1))
    player = relationship("Player", back_populates="handicaps")

    def playing_handicap(self, event):
        return calc_playing_handicap_for_event(self.handicap, event)

    def __repr__(self):
        return '<Handicap - Player: {}, Date: {}, Status: {}, Handicap: {}>'.format(self.player.full_name(), self.date,
                                                                                    self.status.name, self.handicap)


class Score(Base):
    __tablename__ = "scores"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    position = Column(Integer, nullable=False)
    shots = Column(Integer, nullable=False)
    points = Column(Integer, nullable=False)
    card = Column(IntArray(60))
    player = relationship("Player", back_populates="scores")
    event = relationship("Event", back_populates="scores")

    def __repr__(self):
        return '<Score - Event: {}, Player: {}>'.format(self.event, self.player.full_name())


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    member_id = Column(Integer, ForeignKey('members.id'), nullable=False)
    date = Column(Date, nullable=False)
    playing = Column(Boolean, nullable=False)
    comment = Column(String(100), nullable=True)
    guests = relationship("Guest", back_populates="booking", cascade="all, delete, delete-orphan")
    event = relationship("Event", back_populates="bookings")
    member = relationship("Member", back_populates="bookings")

    def debug_info(self):
        return '<Booking: id:{} event id: {}, member id: {}>'.format(self.id, self.event_id, self.member_id)

    def __repr__(self):
        return '<Booking - Event: {}, Member: {}>'.format(self.event.full_name(), self.member.player.full_name())


class Guest(Base):
    __tablename__ = "guests"
    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey('bookings.id'), nullable=False)
    name = Column(String(100), nullable=False)
    handicap = Column(Numeric(precision=3, scale=1), nullable=False)
    booking = relationship("Booking", back_populates="guests")

    def __repr__(self):
        return '<Guest - Booking: {}, Name: {}, Handicap: {}>'.format(self.booking, self.name, self.handcap)


class User(Base, UserMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'), nullable=False)
    user_name = Column(String(25), nullable=False)
    password = Column(String(100), nullable=False)
    roles = relationship("Role", back_populates="user")
    member = relationship('Member', back_populates="user")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_reset_password_token(self, app, expires_in=600):
        exp = time() + expires_in
        token = jwt.encode(
            {'reset_password': self.id, 'exp': exp},
            app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')
        return token, strftime('%a, %d %b %Y %H:%M:%S +0000', localtime(exp))

    @staticmethod
    def verify_reset_password_token(app, token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return '<User {}>'.format(self.user_name)


class Role(Base):
    __tablename__ = "roles"
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, primary_key=True)
    role = Column(EnumType(UserRole), nullable=False, primary_key=True)
    user = relationship("User", back_populates="roles")

    def __repr__(self):
        return '<Role {}>'.format(self.role.name)

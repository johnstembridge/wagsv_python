import datetime
import string

from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, TextAreaField, SubmitField, FieldList, FormField, HiddenField, RadioField
from wtforms.fields.html5 import DateField
from wtforms.validators import Optional

from back_end.data_utilities import encode_date, fmt_date, fmt_curr, first_or_default, parse_float
from back_end.calc import calc_playing_handicap_for_event
from back_end.interface import get_event, get_booking, save_booking, get_member, get_committee_function_member, \
    get_player_by_name, suspend_flush

from front_end.form_helpers import line_break
from globals.email import send_mail
from globals.enumerations import Function, PlayerStatus, EventType, EventBooking
from models.wags_db import Guest, Contact
from wags_user import app


class GuestForm(FlaskForm):
    item_pos = HiddenField(label='Item_pos')
    guest_name = StringField('Name', validators=[Optional()])
    handicap = StringField('Handicap')


class EventDetailsForm(FlaskForm):
    bookable = HiddenField(label='Bookable')
    at_capacity = HiddenField(label='At Capacity')
    show_bookings = HiddenField(label='Show Bookings')
    message = StringField(label='Message')
    title = StringField(label='Title')
    event = StringField(label='Event')
    date = StringField(label='Date')
    venue = StringField(label='Venue')
    venue_address = StringField(label='Address')
    venue_phone = StringField(label='Phone')
    map_url = StringField(label='map_url')
    schedule = TextAreaField(label='Schedule')
    member_price = DecimalField(label='Members')
    guest_price = StringField(label='Guests')
    organiser = StringField(label='Organiser')
    organiser_id = StringField(label='Organiser Id')
    booking_deadline = StringField(label='Booking deadline')
    venue_directions = StringField(label='directions')
    notes = StringField(label='Notes', default='')
    member_name = StringField(label='Member Name')
    booking_date = DateField(label='Booking Date')
    attend = RadioField('Attending', choices=[(1, 'will attend'), (0, 'will not attend')], coerce=int)
    guests = FieldList(FormField(GuestForm))
    comment = TextAreaField(label='Comments')

    event_id = HiddenField(label='Event Id')
    event_type = HiddenField(label='Event Type')
    max_guests = HiddenField(label='Max Guests per Member')

    submit = SubmitField(label='Save')

    def populate_event(self, event_id, member_id):
        event = get_event(event_id)
        self.bookable.data = event.is_bookable()
        self.at_capacity.data = event.at_capacity()
        if self.bookable.data:
            self.title.data = 'Book Event'
        else:
            self.title.data = 'Event Details'
        self.show_bookings.data = event.bookable() in [EventBooking.open, EventBooking.viewable] and \
                                  len(event.bookings) > 0
        self.event_id.data = event_id
        self.event_type.data = event.type
        self.date.data = encode_date(event.date)
        if event.organiser:
            self.organiser_id.data = event.organiser.id
            self.organiser.data = event.organiser.player.full_name()
        else:
            self.organiser_id.data = 0
        self.event.data = event.trophy.name if event.trophy else event.venue.name
        self.venue.data = event.venue.name
        contact = event.venue.contact or Contact()
        post_code = contact.post_code or ''
        self.venue_address.data = line_break((contact.address or '') + ',' + post_code, [',', '\r', '\n'])
        self.venue_phone.data = contact.phone or ''
        self.map_url.data = 'http://maps.google.co.uk/maps?q={}&title={}&z=12 target="googlemap"' \
            .format(post_code.replace(' ', '+'), event.venue.name)
        self.venue_directions.data = line_break(event.venue.directions or '', '\n')
        self.schedule.data = line_break([(s.time.strftime('%H:%M ') + s.text) for s in event.schedule])
        self.member_price.data = event.member_price
        if event.max_guests == 0:
            self.guest_price.data = 'This event is members only'
        else:
            self.guest_price.data = fmt_curr(event.guest_price)
        self.max_guests.data = event.max_guests
        self.booking_deadline.data = encode_date(event.booking_end)
        self.notes.data = event.note or ''

        if member_id == 0:
            self.message.data = ''
            return

        booking = get_booking(event_id, member_id)
        if not booking.id:
            booking.member = get_member(member_id)
            booking.playing = True
        self.message.data = self.booking_message(event, booking)
        if event.is_bookable() or booking.id:
            self.attend.data = booking.playing
            self.comment.data = booking.comment
            self.booking_date.data = fmt_date(booking.date)
            self.member_name.data = booking.member.player.full_name()

            count = 1
            max = event.max_guests
            for guest in booking.guests + (max - len(booking.guests)) * [Guest()]:
                item_form = GuestForm()
                item_form.item_pos = count
                item_form.guest_name = guest.name
                item_form.handicap = guest.handicap
                self.guests.append_entry(item_form)
                count += 1

    @staticmethod
    def booking_message(event, booking):
        if event.type == EventType.cancelled:
            return 'This event has been cancelled'
        if event.bookable() == EventBooking.not_applicable or event.type == EventType.wags_tour:
            return 'Booking is not available for this event'
        today = datetime.date.today()
        booking_start = event.booking_start or event.date
        booking_end = event.booking_end or event.date
        if today > booking_end:
            return 'Booking is now closed for this event'
        if booking_start > today:
            return 'Booking is not yet open for this event'
        if booking.id:
            return 'You responded on {} - see below for details'.format(fmt_date(booking.date))
        if event.at_capacity():
            return 'Event is at capacity' \
                   + (': Please contact the organiser to go on the reserve list.' if event.has_reserve_list() else '.')
        return ''

    def book_event(self, event_id, member_id):
        errors = self.errors
        if len(errors) > 0:
            return False
        booking = get_booking(event_id, member_id)
        with suspend_flush():
            booking.date = datetime.date.today()
            booking.playing = self.attend.data
            booking.comment = self.comment.data if len(self.comment.data) > 0 else None
            guests = []
            if booking.playing:
                for guest in self.guests:
                    name = string.capwords(guest.guest_name.data)
                    if len(name) > 0:
                        obj = first_or_default([g for g in booking.guests if g.name == name],
                                               Guest(name=name, booking=booking))
                        hcap = parse_float(guest.handicap.data, 28.0)
                        known_player = get_player_by_name(name)
                        if known_player:
                            state = known_player.state_as_of(booking.date)
                            if state.status == PlayerStatus.member:
                                hcap = state.handicap
                        obj.handicap = hcap
                        guests.append(obj)
            booking.guests = guests
            app.logger.info(booking.debug_info())
        save_booking(booking)

        return self.confirm_booking(event_id, member_id)

    @staticmethod
    def confirm_booking(event_id, member_id):
        booking = get_booking(event_id, member_id)
        event = booking.event
        subject = 'Book event - {}'.format(event.full_name())
        cost = 0
        if booking.playing:
            cost += event.member_price
            hcap = booking.member.player.state_as_of(booking.date).handicap
            message = ['{} will attend'.format(booking.member.player.full_name()),
                       'The handicap(s) shown below are Playing Handicap and (WHS) where the Playing Handicap '
                       'is 95% of your WHS handicap factored by the slope index of the course',
                       'Your handicap: {} ({})'.format(calc_playing_handicap_for_event(hcap, event), hcap)]
            if booking.guests:
                message.append('Guests:')
                for guest in booking.guests:
                    cost += event.guest_price
                    message.append(
                        '{} {} ({})'.format(guest.name, calc_playing_handicap_for_event(guest.handicap, event), guest.handicap))
            message.append('Total cost £{}'.format(cost))
            message.append(
                '(Please pay by on-line credit to the WAGS bank account number 01284487, sort code 40-07-30)')
            if booking.comment:
                message.append(booking.comment)
        else:
            message = ['{} will not attend'.format(booking.member.player.full_name())]
        sender = 'booking@wags.org'
        to = booking.member.contact.email
        organiser = event.organiser.contact.email
        fixtures = get_committee_function_member(Function.Fixtures).member.contact.email
        treasurer = get_committee_function_member(Function.Treasurer).member.contact.email
        send_mail(to=to,
                  sender=sender,
                  cc=[organiser, fixtures, treasurer],
                  subject='WAGS: ' + subject,
                  message=message)
        message.append('A confirmation email has been sent to {}'.format(to))
        message.append('If it does not appear in your inbox, check your spam/junk folder')
        form = EventBookingConfirmationForm()
        form.populate(subject, message)
        return form


class EventBookingConfirmationForm(FlaskForm):
    title = StringField(label='Title')
    message = StringField(label='Message')

    def populate(self, title, message):
        self.title.data = title
        self.message.data = message

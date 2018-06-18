import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, TextAreaField, SubmitField, FieldList, FormField, HiddenField, RadioField
from wtforms.fields.html5 import DateField
from wtforms.validators import Optional

from back_end.data_utilities import encode_date, fmt_date, first_or_default, to_bool
from back_end.interface import get_event, get_booking, save_booking, is_event_bookable, get_member
from front_end.form_helpers import line_break
from models.wags_db import Guest, Booking


class GuestForm(FlaskForm):
    item_pos = HiddenField(label='Item_pos')
    guest_name = StringField('Name', validators=[Optional()])
    handicap = StringField('Handicap')


class EventDetailsForm(FlaskForm):
    bookable = HiddenField(label='Bookable')
    title = StringField(label='Title')
    event = StringField(label='Event')
    date = StringField(label='Date')
    venue = StringField(label='Venue')
    venue_address = StringField(label='Address')
    venue_phone = StringField(label='Phone')
    map_url = StringField(label='map_url')
    schedule = TextAreaField(label='Schedule')
    member_price = DecimalField(label='Members')
    guest_price = DecimalField(label='Guests')
    organiser = StringField(label='Organiser')
    organiser_id = StringField(label='Organiser Id')
    booking_deadline = StringField(label='Booking deadline')
    venue_directions = StringField(label='directions')
    notes = StringField(label='Notes', default='')
    member_name = StringField(label='Member Name')
    booking_date = DateField(label='Booking Date')
    attend = RadioField('Attending', choices=[(True, 'will attend'), (False, 'will not attend')], coerce=to_bool)
    guests = FieldList(FormField(GuestForm))
    comment = TextAreaField(label='Comments')

    event_id = HiddenField(label='Event Id')
    event_type = HiddenField(label='Event Type')

    submit = SubmitField(label='Save')

    def populate_event(self, event_id, member_id):
        event = get_event(event_id)
        self.bookable.data = is_event_bookable(event)
        if self.bookable.data:
            self.title.data = 'Book Event'
        else:
            self.title.data = 'Event Details'
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
        post_code = event.venue.contact.post_code or ''
        self.venue_address.data = line_break(event.venue.contact.address or '' + ',' + post_code, ',')
        self.venue_phone.data = event.venue.contact.phone
        self.map_url.data = 'http://maps.google.co.uk/maps?q={}&title={}&z=12 target="googlemap"'\
            .format(post_code.replace(' ', '+'), event.venue.name)
        self.venue_directions.data = line_break(event.venue.directions or '', '\n')
        self.schedule.data = line_break([(s.time.strftime('%H:%M ') + s.text)for s in event.schedule])
        self.member_price.data = event.member_price
        self.guest_price.data = event.guest_price
        self.booking_deadline.data = encode_date(event.booking_end)
        self.notes.data = event.note or ''

        booking = get_booking(event_id, member_id)
        if booking is None:
            booking = Booking(member=get_member(member_id), playing=True)
        else:
            self.booking_date.data = fmt_date(booking.date)
            self.attend.data = booking.playing
            self.comment.data = booking.comment
        self.member_name.data = booking.member.player.full_name()
        count = 1
        for guest in booking.guests + (3 - len(booking.guests)) * [Guest()]:
            item_form = GuestForm()
            item_form.item_pos = count
            item_form.guest_name = guest.name
            item_form.handicap = guest.handicap
            self.guests.append_entry(item_form)
            count += 1

    def save_event(self, event_id, member_id):
        errors = self.errors
        if len(errors) > 0:
            return False
        booking = get_booking(event_id, member_id) or Booking(event_id=event_id, member_id=member_id)
        booking.date = datetime.date.today()
        booking.playing = self.attend.data
        booking.comment = self.comment.data if len(self.comment.data) > 0 else None
        guests = []
        for guest in self.guests:
            name = guest.guest_name.data
            if len(name) > 0:
                obj = first_or_default([g for g in booking.guests if g.name == name], Guest(name=name))
                obj.handicap = guest.handicap
                guests.append(obj)
        booking.guests = guests
        save_booking(booking)

        return True

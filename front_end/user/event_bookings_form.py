import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, FieldList, FormField
from back_end.data_utilities import fmt_date
from back_end.interface import get_event


class BookingItemForm(FlaskForm):
    date = StringField(label='Date')
    member_name = StringField(label='Name')
    number = StringField(label='Number')
    guests = StringField(label='Guests')
    comment = StringField(label='Comment')


class EventBookingsForm(FlaskForm):
    event_name = StringField(label='Event Name')
    sub_title = StringField(label='SubTitle')
    booking_list = FieldList(FormField(BookingItemForm))
    total = StringField(label='Total')

    def populate_event_bookings(self, event_id):
        event = get_event(event_id)
        self.event_name.data = event.full_name()
        self.sub_title.data = 'to date' if datetime.date.today() < event.booking_end else ''
        total = 0
        for booking in event.bookings:
            item_form = BookingItemForm()
            item_form.date = fmt_date(booking.date)
            item_form.member_name = booking.member.player.full_name()
            if booking.playing:
                number = 1 + len(booking.guests)
                item_form.number = number
                total += number
                item_form.guests = ', '.join([g.name + ' ({})'.format(g.handicap) for g in booking.guests])
                item_form.comment = booking.comment or ''
                self.booking_list.append_entry(item_form)
        self.total.data = total


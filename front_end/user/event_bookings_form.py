import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, FieldList, FormField
from back_end.data_utilities import fmt_date
from back_end.interface import get_event, get_player_by_name, add_player, new_handicap
from globals.enumerations import PlayerStatus, EventType


class BookingItemForm(FlaskForm):
    date = StringField(label='Date')
    member_name = StringField(label='Name')
    hcap = StringField(label='Playing handicap')
    number = StringField(label='Number')
    guests = StringField(label='Guests')
    comment = StringField(label='Comment')


class EventBookingsForm(FlaskForm):
    event_name = StringField(label='Event Name')
    slope = StringField(label='Course slope rating')
    sub_title = StringField(label='SubTitle')
    booking_list = FieldList(FormField(BookingItemForm))
    total = StringField(label='Total')

    def populate_event_bookings(self, event_id):
        event = get_event(event_id)
        tour = event.type == EventType.wags_tour
        self.event_name.data = event.full_name()
        self.sub_title.data = 'to date' if datetime.date.today() <= event.booking_end else ''
        cd = None if tour else event.course.course_data_as_of(event.date.year)
        self.slope.data = None if tour else cd.slope
        total = 0
        for booking in event.bookings:
            item_form = BookingItemForm()
            item_form.date = fmt_date(booking.date)
            item_form.member_name = booking.member.player.full_name()
            if booking.playing:
                item_form.hcap = 'n/a' if tour else booking.member.player.state_as_of(event.date).playing_handicap(event)
                number = 1 + len(booking.guests)
                item_form.number = number
                total += number
                item_form.guests = ''
                for g in booking.guests:
                    p = get_player_by_name(g.name)
                    if p:
                        state = p.state_as_of(event.date)
                        if state.handicap == 0 or not state.status.current_member() and state.date < event.date:
                            p.handicaps.append(
                                new_handicap(p, status=state.status, handicap=g.handicap, date=event.date))
                    else:
                        p = add_player(name=g.name, hcap=g.handicap, status=PlayerStatus.guest, date=event.date,
                                       commit=False)
                    hcap = p.state_as_of(event.date).playing_handicap(event)
                    item_form.guests += ',' + g.name + ' ({})'.format(hcap)
                item_form.guests = item_form.guests[1:]
                item_form.comment = booking.comment or ''
                self.booking_list.append_entry(item_form)
        self.total.data = total

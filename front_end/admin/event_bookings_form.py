from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FieldList, FormField, HiddenField, BooleanField

from back_end.interface import get_event, save_event_booking, get_player_by_name
from back_end.data_utilities import fmt_date
from back_end.table import Table
from globals import enumerations

class EventBookingItemForm(FlaskForm):
    date = StringField(label='Date')
    player_name = StringField(label='Name')
    guest = HiddenField(label='Guest')
    guest_id = HiddenField(label='Guest Name')
    playing = BooleanField(label='Playing?')
    playing_hcap = StringField(label='Playing handicap')
    whs_hcap = StringField(label='WHS handicap')
    comment = StringField(label='Comment')
    member_id = HiddenField(label='member id')
    booking_id = HiddenField(label='booking id')

class EventBookingsForm(FlaskForm):
    bookings = FieldList(FormField(EventBookingItemForm))
    save_bookings = SubmitField(label='Save')
    editable = HiddenField(label='Editable')
    event_id = HiddenField(label='Event_id')
    event_name = StringField(label='event_name')
    add_player = SubmitField(label='Add Player')

    def populate_event_bookings(self, event_id):
        self.event_id.data = event_id
        event = get_event(event_id)
        tour = event.type == enumerations.EventType.wags_tour
        self.event_name.data = event.full_name()
        self.editable.data = event.is_booking_editable()
        if event.tour_event_id:
            bookings = get_event(event.tour_event_id).bookings
        else:
            bookings = event.bookings
        for booking in bookings:
            item_form = EventBookingItemForm()
            item_form.date = fmt_date(booking.date)
            item_form.player_name = booking.member.player.full_name()
            item_form.guest.data = False
            state = booking.member.player.state_as_of(event.date)
            item_form.playing_hcap = 'n/a' if tour else state.playing_handicap(event)
            item_form.whs_hcap = ""
            item_form.playing = booking.playing
            item_form.comment = booking.comment
            item_form.member_id = booking.member_id
            item_form.booking_id = booking.id
            self.bookings.append_entry(item_form)
            for g in booking.guests:
                item_form = EventBookingItemForm()
                item_form.guest.data = True
                item_form.guest_id = g.id
                item_form.date = "..guest"
                item_form.player_name = g.name
                player=get_player_by_name(g.name)
                if player:
                    state = player.state_as_of(event.date)
                    item_form.playing_hcap = 'n/a' if tour else state.playing_handicap(event)
                    item_form.comment = ""
                else:
                    item_form.comment = "*** not found - check name spelling ***"
                item_form.whs_hcap = g.handicap
                item_form.playing.data = booking.playing
                item_form.member_id = booking.member_id
                item_form.booking_id = booking.id
                self.bookings.append_entry(item_form)

    def save_event_bookings(self, event_id):
        errors = self.errors
        if len(errors) > 0:
            return False

        fields = ['member_id', 'booking_id', 'playing', 'guest_id', 'name', 'hcap']
        form_fields = ['member_id', 'booking_id', 'playing', 'guest_id', 'player_name', 'whs_hcap']

        def sel_table_fields(dict, fields):
            res = []
            for i in range(len(fields)):
                res.append(dict[fields[i]])
            return res

        bookings = Table(fields, [sel_table_fields(s, form_fields) for s in self.data['bookings']])
        save_event_booking(event_id, bookings)
        return True
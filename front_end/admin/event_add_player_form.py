from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, SelectField

from back_end.interface import get_event, get_member_select_choices, get_booking, save_booking, get_players_for_event
from front_end.form_helpers import set_select_field_new
from models.wags_db import Guest


class AddPlayerForm(FlaskForm):
    event_name = StringField(label='event_name')
    member = SelectField(label='Member')
    guest_name = StringField(label='Guest Name')
    guest_handicap = StringField(label='Handicap')
    submit = SubmitField(label='Submit')
    event_id = HiddenField(label='Event_id')

    def populate_add_player(self, event_id, member_id):
        self.event_id.data = event_id
        self.event_name.data = get_event(event_id).full_name()
        set_select_field_new(self.member, get_member_select_choices(), default_selection=member_id, item_name='Member')

    def add_booking(self, event_id, member_id):
        errors = self.errors
        if len(errors) > 0:
            return False
        member = int(self.member.data)
        guest_name = self.guest_name.data
        guest_handicap = float(self.guest_handicap.data or '0')
        if member == 0:
            member = member_id
        booking = get_booking(event_id, member)

        if guest_name != '':
            all_players = get_players_for_event(booking.event)
            if len([x for x in all_players if x.full_name() == guest_name]) > 0:
                return False  # already there
            if guest_handicap == 0:
                return False  # no handicap
            else:
                guest = Guest(name=guest_name, handicap=guest_handicap)
                booking.guests.append(guest)
        else:
            booking.playing = True
        booking.comment = 'Added to enter score'
        save_booking(booking, add=True)
        return True

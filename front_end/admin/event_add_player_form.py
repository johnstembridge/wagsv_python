from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, SelectField

from back_end.interface import get_event, get_member_select_choices, get_booking, save_booking, \
    get_players_for_event_id, get_member, suspend_flush
from front_end.form_helpers import set_select_field_new
from models.wags_db import Guest


class AddPlayerForm(FlaskForm):
    event_name = StringField(label='event_name')
    member = SelectField(label='Member')
    guest_name = StringField(label='Guest Name')
    guest_handicap = StringField(label='Handicap')
    submit = SubmitField(label='Submit')
    event_id = HiddenField(label='Event_id')
    members_only = HiddenField(label='Members Only')

    def populate_add_player(self, event_id):
        self.event_id.data = event_id
        self.event_name.data = get_event(event_id).full_name()
        set_select_field_new(self.member, get_member_select_choices(), item_name='Member')
        self.members_only.data = get_event(event_id).max_guests == 0

    def add_booking(self, event_id):
        errors = self.errors
        if len(errors) > 0:
            return False
        member_id = int(self.member.data)
        if member_id == 0:
            flash('No member given for booking', 'danger')
            return True
        booking = get_booking(event_id, member_id)
        with suspend_flush():
            if not booking.id:
                # new booking for member
                booking.member = get_member(member_id)
                booking.playing = True
            guest_name = self.guest_name.data
            guest = guest_name != ''
            if guest:
                player_name = guest_name.title()
                guest_handicap = float(self.guest_handicap.data or '0')
            else:
                player_name = booking.member.player.full_name()
            all_players = [x.full_name() for x in get_players_for_event_id(event_id)]
            if player_name in all_players:
                flash('{} is already in the list of players for this event'.format(player_name), 'danger')
                return False
            if guest:
                if guest_handicap == 0:
                    flash('No handicap given for {}'.format(guest_name), 'danger')
                    return False
                else:
                    g = Guest(name=guest_name, handicap=guest_handicap)
                    booking.guests.append(g)
            else:
                booking.playing = True
            booking.comment = 'Added to enter score'
        save_booking(booking)
        flash('{} added to player list for this event'.format(player_name), 'success')
        return True

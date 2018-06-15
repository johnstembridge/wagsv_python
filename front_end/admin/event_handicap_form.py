import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FieldList, FormField, HiddenField

from back_end.data_utilities import fmt_date
from back_end.interface import get_event, save_handicaps, is_last_event, sorted_players_for_event
from back_end.table import Table
from globals.enumerations import PlayerStatus


class EventHandicapItemForm(FlaskForm):
    num = IntegerField(label='id')
    position = IntegerField(label='Position')
    player = StringField(label='Player')
    strokes = IntegerField(label='Strokes')
    points = IntegerField(label='Points')
    guest = StringField(label='Guest')
    handicap = StringField(label='Handicap')
    player_id = HiddenField(label='Player_id')
    status_return = HiddenField(label='Guest')
    old_handicap = HiddenField(label='Old_Handicap')


class EventHandicapsForm(FlaskForm):
    scores = FieldList(FormField(EventHandicapItemForm))
    event_name = StringField(label='event_name')
    new_date = StringField(label='new_date')
    save_handicaps = SubmitField(label='Save')
    editable = HiddenField(label='Editable')
    event_id = HiddenField(label='Event_id')

    def populate_event_handicaps(self, event_id):
        self.event_id.data = event_id
        event = get_event(event_id)
        self.event_name.data = event.full_name()
        new_date = event.date + datetime.timedelta(days=1)
        self.new_date.data = fmt_date(new_date)
        self.editable.data = is_last_event(event)
        num = 0
        for player in sorted_players_for_event(event):
            num += 1
            item_form = EventHandicapItemForm()
            item_form.num = str(num)
            state = player.state_as_of(new_date)
            guest = " (guest)" if (state.status == PlayerStatus.guest) else ""
            item_form.player = player.full_name() + guest
            item_form.handicap = state.handicap
            score = player.score_for(event.id)
            item_form.points = score.points
            item_form.strokes = score.shots
            item_form.position = score.position
            item_form.player_id = player.id
            item_form.status_return = state.status.value
            item_form.old_handicap = state.handicap
            self.scores.append_entry(item_form)

    def save_event_handicaps(self, event_id):
        errors = self.errors
        if len(errors) > 0:
            return False
        date = get_event(event_id).date + datetime.timedelta(days=1)
        fields = ['player_id', 'date', 'status', 'handicap']
        data = [[int(d['player_id']), date, PlayerStatus(int(d['status_return'])), float(d['handicap'])]
                for d in self.data['scores'] if d['handicap'] != d['old_handicap']]

        save_handicaps(Table(fields, data))
        return True

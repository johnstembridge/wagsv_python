import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FieldList, FormField, HiddenField
from back_end.interface import get_event, get_results, save_handicaps, is_last_event
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
    save_handicaps = SubmitField(label='Save')
    editable = HiddenField(label='Editable')
    event_id = HiddenField(label='Event_id')

    def populate_event_handicaps(self, event_id):
        self.event_id.data = event_id
        event = get_event(event_id)
        self.event_name.data = event.full_name()
        self.editable.data = is_last_event(event)
        num = 0
        for player in get_results(event, for_edit_hcap=True):
            num += 1
            item_form = EventHandicapItemForm()
            item_form.num = str(num)
            guest = "" if (player['status'] == PlayerStatus.member) else " (guest)"
            item_form.player = player['player'] + guest
            item_form.points = player['points']
            item_form.strokes = player['strokes']
            item_form.handicap = player['handicap']
            item_form.position = player['position']
            item_form.player_id = player['player_id']
            item_form.status_return = player['status'].value
            item_form.old_handicap = player['handicap']
            self.scores.append_entry(item_form)

    def save_event_handicaps(self):
        errors = self.errors
        if len(errors) > 0:
            return False
        date = datetime.date.today()
        fields = ['player_id', 'date', 'status', 'handicap']
        data = [[int(d['player_id']), date, PlayerStatus(int(d['status_return'])), float(d['handicap'])]
                for d in self.data['scores'] if d['handicap'] != d['old_handicap']]

        save_handicaps(Table(fields, data))
        return True

import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FieldList, FormField, HiddenField

from data_utilities import first_or_default, fmt_date
from interface import get_event, get_results, save_hcaps, get_handicaps, is_latest_event


class EventHandicapItemForm(FlaskForm):
    num = IntegerField(label='id')
    position = IntegerField(label='Position')
    player = StringField(label='Player')
    strokes = IntegerField(label='Strokes')
    points = IntegerField(label='Points')
    guest = StringField(label='Guest')
    handicap = StringField(label='Handicap')
    player_id = HiddenField(label='Player_id')
    guest_return = HiddenField(label='Guest')
    old_handicap = HiddenField(label='Old_Handicap')


class EventHandicapsForm(FlaskForm):
    scores = FieldList(FormField(EventHandicapItemForm))
    event_name = StringField(label='event_name')
    save_handicaps = SubmitField(label='Save')
    editable = HiddenField(label='Editable')
    event_id = HiddenField(label='Event_id')
    year = HiddenField(label='Year')

    def populate_event_handicaps(self, year, event_id):
        self.event_id.data = event_id
        self.year.data = year
        event = get_event(year, event_id)
        self.event_name.data = '{} {} {}'.format(event['event'], event['venue'], event['date'])
        editable = datetime.date.today() > event['date'] and is_latest_event(event_id)
        self.editable.data = 'y' if editable else 'n'
        players = get_results(year, event_id)
        if editable:
            hcaps = get_handicaps(fmt_date(datetime.date.today()))
        else:
            hcaps = None
        num = 0
        for player in players:
            if hcaps:
                hcap = first_or_default([h[1] for h in hcaps if h[0] == str(player['id'])], None)
            else:
                hcap = player['handicap']
            num += 1
            item_form = EventHandicapItemForm()
            item_form.num = str(num)
            guest = "" if (player['guest'] == "") else " (" + player['guest'] + ")"
            item_form.player = player['name'] + guest
            item_form.points = player['points']
            item_form.strokes = player['strokes']
            item_form.handicap = hcap
            item_form.position = player['position']
            item_form.player_id = str(player['id'])
            item_form.guest_return = player['guest']
            item_form.old_handicap = hcap
            self.scores.append_entry(item_form)

    def save_event_handicaps(self):
        errors = self.errors
        if len(errors) > 0:
            return False
        fields = ['player', 'handicap', 'status']
        data = [
            [d['player_id'],
             d['handicap'],
             1 if d['guest_return'] == 'guest' else 0
             ]
            for d in self.data['scores'] if d['handicap'] != d['old_handicap']]
        date = fmt_date(datetime.date.today())
        save_hcaps(date, fields, data)
        return True

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FieldList, FormField, HiddenField

from back_end.data_utilities import fmt_date
from back_end.interface import get_event, get_results, is_event_result_editable


class EventResultItemForm(FlaskForm):
    position = IntegerField(label='Position')
    player = StringField(label='Player')
    handicap = IntegerField(label='Handicap')
    strokes = IntegerField(label='Strokes')
    points = IntegerField(label='Points')
    guest = StringField(label='Guest')
    player_id = HiddenField(label='Player_id')


class EventResultsForm(FlaskForm):
    scores = FieldList(FormField(EventResultItemForm))
    event_name = StringField(label='event_name')
    event_id = HiddenField(label='Event_id')
    date = HiddenField(label='Date')

    def populate_event_results(self, year=None, event_id=None, date=None):
        if date is not None:
            event = get_event(date=date)
            self.event_id.data = None
            players = get_results(date=date)
        else:
            self.event_id.data = event_id
            event = get_event(year=year, event_id=event_id)
            date = fmt_date(event['date'])
            players = get_results(year, event_id=event_id)
        self.date.data = date.replace('/', '-')
        self.event_name.data = '{} {} {}'.format(event['event'], event['venue'], date)
        for player in [p for p in players if int(p['points']) > 0]:
            item_form = EventResultItemForm()
            guest = "" if (player['guest'] == "") else " (" + player['guest'] + ")"
            item_form.player = player['name'] + guest
            item_form.handicap = player['handicap']
            item_form.points = player['points']
            item_form.strokes = player['strokes']
            item_form.position = player['position']
            item_form.guest = player['guest']
            item_form.player_id = str(player['id'])
            self.scores.append_entry(item_form)

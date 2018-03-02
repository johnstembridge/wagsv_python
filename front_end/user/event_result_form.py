from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FieldList, FormField, HiddenField
from back_end.interface import get_event, get_results, save_event_scores, is_event_result_editable


class EventResultItemForm(FlaskForm):
    num = IntegerField(label='id')
    position = IntegerField(label='Position')
    player = StringField(label='Player')
    handicap = IntegerField(label='Handicap')
    strokes = IntegerField(label='Strokes')
    points = IntegerField(label='Points')
    guest = StringField(label='Guest')
    player_id = HiddenField(label='Player_id')
    strokes_return = HiddenField(label='Strokes')
    guest_return = HiddenField(label='Guest')
    handicap_return = HiddenField(label='Handicap')


class EventResultsForm(FlaskForm):
    scores = FieldList(FormField(EventResultItemForm))
    event_name = StringField(label='event_name')
    add_player = SubmitField(label='Add Player')
    save_results = SubmitField(label='Save')
    editable = HiddenField(label='Editable')
    event_id = HiddenField(label='Event_id')
    year = HiddenField(label='Year')

    def populate_event_results(self, year, event_id):
        self.event_id.data = event_id
        self.year.data = year
        event = get_event(year, event_id)
        self.event_name.data = '{} {} {}'.format(event['event'], event['venue'], event['date'])
        self.editable = is_event_result_editable(year, event_id)
        players = get_results(year, event_id)
        num = 0
        for player in players:
            num += 1
            item_form = EventResultItemForm()
            item_form.num = str(num)
            guest = "" if (player['guest'] == "") else " (" + player['guest'] + ")"
            item_form.player = player['name'] + guest
            item_form.handicap = player['handicap']
            item_form.points = player['points']
            item_form.strokes = player['strokes']
            item_form.position = player['position']
            item_form.guest = player['guest']
            item_form.player_id = str(player['id'])
            item_form.guest_return = player['guest']
            item_form.handicap_return = player['handicap']
            item_form.strokes_return = player['strokes']
            self.scores.append_entry(item_form)

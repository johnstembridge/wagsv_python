from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FieldList, FormField, HiddenField

from back_end.interface import get_event, get_results, save_event_scores, is_event_result_editable, add_player, \
    update_trophy_history, get_booked_players
from back_end.calc import calc_event_positions
from back_end.table import Table


class EventResultItemForm(FlaskForm):
    position = IntegerField(label='Position')
    player = StringField(label='Player')
    handicap = IntegerField(label='Handicap')
    strokes = IntegerField(label='Strokes')
    points = IntegerField(label='Points')
    guest = StringField(label='Guest')
    player_id = HiddenField()
    handicap_return = HiddenField()
    strokes_return = HiddenField()
    guest_return = HiddenField()


class EventResultsForm(FlaskForm):
    scores = FieldList(FormField(EventResultItemForm))
    event_name = StringField(label='event_name')
    add_player = SubmitField(label='Add Player')
    save_results = SubmitField(label='Save')
    editable = HiddenField(label='Editable')
    event_id = HiddenField(label='Event_id')

    def populate_event_results(self, event_id):
        self.event_id.data = event_id
        event = get_event(event_id)
        self.event_name.data = event.full_name()
        self.editable.data = is_event_result_editable(event)
        for player in get_results(event):
            item_form = EventResultItemForm()
            item_form.player = player['player']
            item_form.handicap = player['handicap']
            item_form.handicap_return = player['handicap']
            item_form.points = player['points']
            item_form.strokes = player['strokes']
            item_form.strokes_return = player['strokes']
            item_form.position = player['position']
            item_form.player_id = player['player_id']
            self.scores.append_entry(item_form)

    def save_event_results(self, year, event_id):
        errors = self.errors
        if len(errors) > 0:
            return False

        fields = ['player', 'position', 'points', 'strokes', 'handicap', 'status']
        old_fields = ['player_id', 'position', 'points', 'strokes_return', 'handicap_return', 'guest_return']

        def sel_table_fields(dict, fields):
            res = []
            for i in range(len(fields)):
                res.append(dict[fields[i]])
            return res
        result = Table(fields, [sel_table_fields(s, old_fields) for s in self.data['scores']])
        result = calc_event_positions(year, event_id, result)

        def sel_fn(values):
            return values['points'] > 0

        result = result.select_rows(sel_fn)
        save_event_scores(year, event_id, result)
        update_trophy_history(year, event_id, result)
        return True

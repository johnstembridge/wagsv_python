from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FieldList, FormField, HiddenField

from back_end.interface import get_event, get_results, save_event_result, is_event_result_editable, add_player, \
    update_trophy_history
from back_end.calc import calc_event_positions
from back_end.table import Table
from globals.enumerations import PlayerStatus


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
    status_return = HiddenField()


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
            if player['player_id'] == 0:
                player['player_id'] = (add_player(player['player'], player['handicap'], player['status'], event.date)).id
            item_form = EventResultItemForm()
            guest = " (guest)" if (player['status'] == PlayerStatus.guest) else ""
            item_form.player = player['player'] + guest
            item_form.handicap = player['handicap']
            item_form.handicap_return = player['handicap']
            item_form.status_return = player['status'].value
            item_form.points = player['points']
            item_form.strokes = player['strokes']
            item_form.strokes_return = player['strokes']
            item_form.position = player['position']
            item_form.player_id = player['player_id']
            self.scores.append_entry(item_form)

    def save_event_results(self, event_id):
        errors = self.errors
        if len(errors) > 0:
            return False

        fields = ['player_id', 'position', 'points', 'shots', 'handicap', 'status']
        old_fields = ['player_id', 'position', 'points', 'strokes_return', 'handicap_return', 'status_return']

        def sel_table_fields(dict, fields):
            res = []
            for i in range(len(fields)):
                res.append(dict[fields[i]])
            return res
        result = Table(fields, [sel_table_fields(s, old_fields) for s in self.data['scores']])
        result = calc_event_positions(event_id, result)

        def sel_fn(values):
            return values['points'] > 0

        result = result.select_rows(sel_fn)
        save_event_result(event_id, result)
        return True

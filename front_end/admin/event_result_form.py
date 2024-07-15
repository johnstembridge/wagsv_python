from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FieldList, FormField, HiddenField

from back_end.interface import get_event, save_event_result, sorted_players_for_event, calc_event_positions
from back_end.table import Table


class EventResultItemForm(FlaskForm):
    position = IntegerField(label='Position')
    player = StringField(label='Player')
    handicap = IntegerField(label='Handicap')
    strokes = IntegerField(label='Strokes')
    points = IntegerField(label='Points')
    guest = StringField(label='Guest')
    player_id = HiddenField()
    whs_handicap = HiddenField()
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
        self.editable.data = event.is_result_editable()
        for player in sorted_players_for_event(event):
            item_form = EventResultItemForm()
            state = player.state_as_of(event.date)
            playing_handicap = state.playing_handicap(event)
            item_form.player = player.full_name() + state.status.qualify()
            item_form.handicap = playing_handicap
            item_form.handicap_return = playing_handicap
            item_form.whs_handicap = float(state.handicap)
            score = player.score_for(event.id)
            item_form.points = score.points
            item_form.strokes = score.shots
            item_form.strokes_return = score.shots
            item_form.position = score.position
            item_form.player_id = player.id
            item_form.status_return = state.status.value
            self.scores.append_entry(item_form)

    def save_event_results(self, event_id):
        errors = self.errors
        if len(errors) > 0:
            return False

        fields = ['player_id', 'position', 'points', 'shots', 'handicap', 'status', 'whs']
        form_fields = ['player_id', 'position', 'points', 'strokes_return', 'handicap_return', 'status_return',
                       'whs_handicap']

        def sel_table_fields(dict, fields):
            res = []
            for i in range(len(fields)):
                res.append(dict[fields[i]])
            return res

        result = Table(fields, [sel_table_fields(s, form_fields) for s in self.data['scores']])
        result = calc_event_positions(event_id, result)

        def sel_fn(values):
            return values['points'] > 0

        result = result.select_rows(sel_fn)
        save_event_result(event_id, result)
        return True

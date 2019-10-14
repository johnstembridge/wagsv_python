from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FieldList, FormField, HiddenField

from back_end.interface import get_event
from globals.enumerations import PlayerStatus
from back_end.data_utilities import fmt_num


class EventResultItemForm(FlaskForm):
    position = IntegerField(label='Position')
    player = StringField(label='Player')
    handicap = IntegerField(label='Handicap')
    strokes = IntegerField(label='Strokes')
    points = IntegerField(label='Points')
    player_id = HiddenField(label='Player_id')


class EventResultsForm(FlaskForm):
    scores = FieldList(FormField(EventResultItemForm))
    event_name = StringField(label='event_name')
    event_id = HiddenField(label='Event_id')

    def populate_event_results(self, event_id):
        event = get_event(event_id)
        self.event_id.data = event_id
        self.event_name.data = event.full_name()
        for score in [s for s in event.scores if s.points > 0]:
            item_form = EventResultItemForm()
            player = score.player
            state = player.state_as_of(event.date)
            if state.status != PlayerStatus.member:
                status = " (" + state.status.name + ")"
            else:
                status = ""
            item_form.player = player.full_name() + status
            item_form.handicap = fmt_num(state.handicap)
            item_form.points = score.points
            item_form.strokes = score.shots
            item_form.position = score.position
            item_form.player_id = player.id
            self.scores.append_entry(item_form)

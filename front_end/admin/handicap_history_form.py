from flask_wtf import FlaskForm
from wtforms import StringField, FormField, FieldList
from wtforms.fields.html5 import DateField
import datetime
from back_end.interface import get_player, is_last_event, get_event


class HandicapItemForm(FlaskForm):
    date = DateField(label='Date')
    handicap = StringField(label='Handicap')
    status = StringField(label='Status')


class HandicapHistoryForm(FlaskForm):
    player = StringField(label='Player')
    history = FieldList(FormField(HandicapItemForm))

    def populate_history(self, event_id, player_id):
        event = get_event(event_id)
        if is_last_event(event):
            date = datetime.date.today()
        else:
            date = event.date
        player = get_player(player_id)
        self.player.data = player.full_name()
        for state in player.state_up_to(date):
            item_form = HandicapItemForm()
            item_form.date = state.date
            item_form.handicap = state.handicap
            item_form.status = state.status.name
            self.history.append_entry(item_form)


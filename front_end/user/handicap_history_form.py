from flask_wtf import FlaskForm
from wtforms import StringField, FormField, FieldList
from wtforms.fields.html5 import DateField

from back_end.data_utilities import fmt_date
from back_end.interface import get_player, get_event


class HandicapItemForm(FlaskForm):
    date = StringField(label='Date')
    handicap = StringField(label='Handicap')
    status = StringField(label='Status')


class HandicapHistoryForm(FlaskForm):
    player = StringField(label='Player')
    history = FieldList(FormField(HandicapItemForm))

    def populate_history(self, player_id, event_id):
        player = get_player(player_id)
        event = get_event(event_id)
        self.player.data = player.full_name()
        for item in player.state_up_to(event.date):
            item_form = HandicapItemForm()
            item_form.date = fmt_date(item.date)
            item_form.handicap = item.handicap
            item_form.status = item.status.name
            self.history.append_entry(item_form)


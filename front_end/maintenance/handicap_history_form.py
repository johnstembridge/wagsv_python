from flask_wtf import FlaskForm
from wtforms import StringField, FormField, FieldList
from wtforms.fields.html5 import DateField
from interface import get_player_name, get_handicap_history,event_date


class HandicapItemForm(FlaskForm):
    date = DateField(label='Date')
    handicap = StringField(label='Handicap')
    status = StringField(label='Status')


class HandicapHistoryForm(FlaskForm):
    player = StringField(label='Player')
    history = FieldList(FormField(HandicapItemForm))

    def populate_history(self, year, event_id, player_id):
        date = event_date(year, event_id)
        self.player.data = get_player_name(player_id)
        for item in get_handicap_history(player_id, date):
            item_form = HandicapItemForm()
            item_form.date = item[0]
            item_form.handicap = item[1]
            item_form.status = '' if item[2] == '1' else 'guest'
            self.history.append_entry(item_form)

from flask_wtf import FlaskForm
from wtforms import StringField, FormField, FieldList
from wtforms.fields.html5 import DateField
from back_end.interface import get_player_name, get_player_id, get_handicap_history
from data_utilities import is_num, normalise_name


class HandicapItemForm(FlaskForm):
    date = DateField(label='Date')
    handicap = StringField(label='Handicap')
    status = StringField(label='Status')


class HandicapHistoryForm(FlaskForm):
    player = StringField(label='Player')
    history = FieldList(FormField(HandicapItemForm))

    def populate_history(self, player_id, date):
        if not is_num(player_id):
            player_id = get_player_id(normalise_name(player_id))
        self.player.data = get_player_name(player_id)
        for item in get_handicap_history(player_id, date):
            item_form = HandicapItemForm()
            item_form.date = item[0]
            item_form.handicap = item[1]
            item_form.status = 'member' if item[2] == '1' else 'guest'
            self.history.append_entry(item_form)


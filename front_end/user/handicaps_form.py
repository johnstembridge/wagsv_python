import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, FieldList, FormField, HiddenField
from back_end.interface import get_current_members_as_players


class HandicapItemForm(FlaskForm):
    item_pos = HiddenField(label='Item_pos')
    player_id = HiddenField(label='Player_id')
    player = StringField(label='Player')
    handicap = StringField(label='Handicap')


class HandicapsForm(FlaskForm):
    handicaps = FieldList(FormField(HandicapItemForm))

    def populate_handicaps(self):
        date = datetime.date.today()
        count = 1
        for player in get_current_members_as_players():
            state = player.state_as_of(date)
            item_form = HandicapItemForm()
            item_form.item_pos = 1 + count % 2
            item_form.player_id = player.id
            item_form.player = player.full_name()
            item_form.handicap = state.handicap
            self.handicaps.append_entry(item_form)
            count += 1


import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, FieldList, FormField, HiddenField, IntegerField, SubmitField
from back_end.interface import get_members_as_players
from back_end.calc import calc_playing_handicap


class HandicapItemForm(FlaskForm):
    item_pos = HiddenField(label='Item_pos')
    player_id = HiddenField(label='Player_id')
    player = StringField(label='Player')
    handicap = StringField(label='Handicap')


class HandicapsForm(FlaskForm):
    slope = IntegerField(label='Slope', default=113)
    calc = SubmitField(label='Calculate')
    handicaps = FieldList(FormField(HandicapItemForm))

    def populate_handicaps(self):
        date = datetime.date.today()
        count = 1
        slope = self.slope.data
        for player in get_members_as_players():
            state = player.state_as_of(date)
            item_form = HandicapItemForm()
            item_form.item_pos = 1 + count % 2
            item_form.player_id = player.id
            item_form.player = player.full_name()
            if slope != 113:
                item_form.handicap = calc_playing_handicap(state.handicap, datetime.date.today().year, slope)
            else:
                item_form.handicap = state.handicap
            self.handicaps.append_entry(item_form)
            count += 1


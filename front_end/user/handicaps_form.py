import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FieldList, FormField, HiddenField
from back_end.data_utilities import first_or_default, fmt_date
from back_end.interface import save_handicaps, get_handicap_records, get_current_members
from globals.enumerations import PlayerStatus


class HandicapItemForm(FlaskForm):
    item_pos = HiddenField(label='Item_pos')
    player_id = HiddenField(label='Player_id')
    player = StringField(label='Player')
    handicap = StringField(label='Handicap')


class HandicapsForm(FlaskForm):
    handicaps = FieldList(FormField(HandicapItemForm))

    def populate_handicaps(self):
        today = datetime.date.today()
        players = get_current_members()
        head, handicaps = get_handicap_records(today)
        rows_per_table = len(players) // 2
        count = 1
        for pid, name in players.items():
            hcap = dict(zip(head, first_or_default([h for h in handicaps if h[1] == str(pid)], [None]*4)))
            # if hcap['status'] == str(PlayerStatus.member):
            item_form = HandicapItemForm()
            item_form.item_pos = 1 if count <= rows_per_table else 2
            item_form.player_id = str(pid)
            item_form.player = name
            item_form.handicap = hcap['handicap']
            self.handicaps.append_entry(item_form)
            count += 1


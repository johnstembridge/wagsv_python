from flask_wtf import FlaskForm
from flask import render_template
from wtforms import StringField, FormField, FieldList, HiddenField

from back_end.interface import get_player_name, get_current_members
from back_end.calc import get_vl
from front_end.utility import render_link


class Vl:

    @staticmethod
    def vl_show(year):
        form = VlForm()
        form.populate_vl(year)
        return render_template('user/vl.html', form=form, render_link=render_link)


class VlItemForm(FlaskForm):
    position = StringField(label='Position')
    player = StringField(label='Player')
    points = StringField(label='Points')
    matches = StringField(label='Matches')
    lowest = StringField(label='Lowest')
    player_id = HiddenField(label='Player_id')


class VlForm(FlaskForm):
    vl = FieldList(FormField(VlItemForm))

    def populate_vl(self, year):
        players = get_current_members()
        vl = get_vl(year)
        for pid, name in players.items():
            item_form = VlItemForm()
            item_form.date = item[0]
            item_form.handicap = item[1]
            item_form.status = '' if item[2] == '1' else 'guest'
            self.history.append_entry(item_form)

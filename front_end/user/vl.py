from flask_wtf import FlaskForm
from flask import render_template
from wtforms import StringField, FormField, FieldList, HiddenField

from back_end.calc import get_vl
from front_end.utility import render_link


class Vl:

    @staticmethod
    def vl_show(year):
        form = VlForm()
        form.populate_vl(year)
        return render_template('user/vl.html', form=form, year=int(year), render_link=render_link)


class VlItemForm(FlaskForm):
    position = StringField(label='Position')
    player = StringField(label='Player')
    points = StringField(label='Points')
    matches = StringField(label='Matches')
    lowest = StringField(label='Lowest')
    player_id = HiddenField(label='Player_id')


class VlForm(FlaskForm):
    vl = FieldList(FormField(VlItemForm))
    year = StringField(label='year')

    def populate_vl(self, year):
        self.year.data = year
        vl = get_vl(year)
        for item in vl.data:
            item_form = VlItemForm()
            item_form.position = item[vl.column_index('position')]
            item_form.player = item[vl.column_index('name')]
            item_form.points = item[vl.column_index('points')]
            item_form.matches = item[vl.column_index('events')]
            item_form.lowest = item[vl.column_index('lowest')]
            item_form.player_id = item[vl.column_index('player')]
            self.vl.append_entry(item_form)
from flask_wtf import FlaskForm
from flask import render_template
from wtforms import StringField, FormField, FieldList, HiddenField

from back_end.interface import get_vl, get_all_vl_winners
from front_end.form_helpers import render_link
from globals.config import url_for_html, url_for_user


class Vl:

    @staticmethod
    def vl_show(year):
        form = VlForm()
        form.populate_vl(year)
        return render_template('user/vl.html', form=form, year=year, render_link=render_link, url_for_user=url_for_user)


    @staticmethod
    def vl_history():
        form = VlHistoryForm()
        form.populate()
        return render_template('user/vl_history.html', form=form, render_link=render_link, url_for_user=url_for_user)


class VlItemForm(FlaskForm):
    position = StringField(label='Position')
    player = StringField(label='Player')
    points = StringField(label='Points')
    matches = StringField(label='Matches')
    lowest = StringField(label='Lowest')
    player_id = HiddenField(label='Player_id')


class VlForm(FlaskForm):
    year = StringField(label='year')
    vl = FieldList(FormField(VlItemForm))

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
            item_form.player_id = item[vl.column_index('player_id')]
            self.vl.append_entry(item_form)


class VlHistoryItemForm(FlaskForm):
    year = StringField(label='year')
    player = StringField(label='Player')
    points = StringField(label='Points')
    matches = StringField(label='Matches')
    lowest = StringField(label='Lowest')
    player_id = HiddenField(label='Player_id')


class VlHistoryForm(FlaskForm):
    image_url = StringField()
    vl = FieldList(FormField(VlHistoryItemForm))

    def populate(self):
        all = get_all_vl_winners()
        self.image_url.data = url_for_html('pictures', 'trophies', 'vl.jpg')
        for vl in all.data:
            item_form = VlHistoryItemForm()
            item_form.year = vl[all.column_index('year')]
            item_form.player = vl[all.column_index('name')]
            item_form.points = vl[all.column_index('points')]
            item_form.matches = vl[all.column_index('events')]
            item_form.lowest = vl[all.column_index('lowest')]
            item_form.player_id = vl[all.column_index('player_id')]
            self.vl.append_entry(item_form)


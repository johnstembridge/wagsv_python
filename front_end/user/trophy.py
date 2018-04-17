import os
from flask_wtf import FlaskForm
from flask import render_template
from wtforms import StringField, FormField, FieldList

from back_end.data_utilities import names_from_ids
from back_end.interface import get_trophy_history, get_player_select_list, get_venue_select_list, get_trophy
from back_end.table import Table
from front_end.form_helpers import render_link
from globals import config


class Trophy:

    @staticmethod
    def trophy_show(trophy_id):
        form = TrophyForm()
        form.populate_trophy(trophy_id)
        return render_template('user/trophy.html', form=form, render_link=render_link)


class TrophyItemForm(FlaskForm):
    date = StringField(label='Date')
    venue = StringField(label='venue')
    winner = StringField(label='Winner')
    score = StringField(label='Score')
    average = StringField(label='Average')


class TrophyForm(FlaskForm):
    winners = FieldList(FormField(TrophyItemForm))
    trophy_name = StringField()
    image_url = StringField()

    def populate_trophy(self, trophy_id):
        trophy = get_trophy(trophy_id)
        self.trophy_name.data = trophy['name']
        self.image_url.data = os.path.join(config.get('locations')['html'], 'trophies', trophy['name'].lower() + '.jpg')
        hist = Table(*get_trophy_history(trophy_id))
        hist.update_column('winner', names_from_ids(get_player_select_list(), hist.get_columns('winner')))
        hist.update_column('venue', names_from_ids(get_venue_select_list(), hist.get_columns('venue')))
        for item in hist.data:
            item_form = TrophyItemForm()
            item_form.venue = item[hist.column_index('venue')]
            item_form.date = item[hist.column_index('date')]
            item_form.winner = item[hist.column_index('winner')]
            item_form.score = item[hist.column_index('score')]
            item_form.average = item[hist.column_index('average')]

            self.winners.append_entry(item_form)
import os
import datetime
from flask_wtf import FlaskForm
from flask import render_template
from wtforms import StringField, FormField, FieldList

from back_end.data_utilities import fmt_date
from back_end.interface import get_trophy
from front_end.form_helpers import render_link, template_exists
from globals import config
from globals.enumerations import EventType


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
    extra = StringField()

    def populate_trophy(self, trophy_id):
        trophy = get_trophy(trophy_id)
        self.trophy_name.data = trophy.name
        self.image_url.data = os.path.join(config.get('locations')['base_url'], 'trophies', trophy.name.lower() + '.jpg')
        hist = trophy.events
        extra_file = 'user/extra/' + trophy.name.lower() + '.htm'
        if template_exists(extra_file):
            self.extra.data = extra_file
        for item in hist:
            if item.date < datetime.date.today():
                item_form = TrophyItemForm()
                item_form.venue = item.venue.name
                item_form.date = fmt_date(item.date)
                item_form.winner = item.winner.full_name()
                if item.type == EventType.wags_vl_event:
                    item_form.score = item.winner.score_for(item.id)
                    item_form.average = item.average_score
                else:
                    item_form.score = item_form.average = ''
                self.winners.append_entry(item_form)

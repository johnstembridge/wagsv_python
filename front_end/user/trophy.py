import datetime
from flask_wtf import FlaskForm
from flask import render_template
from wtforms import StringField, FormField, FieldList

from back_end.data_utilities import fmt_date, first_or_default
from back_end.interface import get_trophy
from front_end.form_helpers import render_link, template_exists
from globals.config import url_for_html, url_for_user
from globals.enumerations import EventType


class Trophy:

    @staticmethod
    def trophy_show(trophy_id):
        form = TrophyForm()
        form.populate_trophy(trophy_id)
        return render_template('user/trophy.html', form=form, render_link=render_link, url_for_user=url_for_user)


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
        self.image_url.data = url_for_html('pictures', 'trophies', trophy.name.lower() + '.jpg')
        extra_file = 'user/extra/' + trophy.name.lower() + '.htm'
        if template_exists(extra_file):
            self.extra.data = extra_file
        hist = trophy.events
        for event in hist:
            tour = first_or_default(
                [e for e in hist if e.date.year == event.date.year and e.type == EventType.wags_tour], None)
            if event.date < datetime.date.today() \
                    and ((event.type == EventType.wags_vl_event and not tour) \
                         or (event.type == EventType.wags_tour and tour)):
                item_form = TrophyItemForm()
                item_form.venue = event.venue.name
                item_form.date = fmt_date(event.date)
                if event.winner:
                    item_form.winner = event.winner.full_name()
                    if event.type == EventType.wags_vl_event:
                        item_form.score = event.winner.score_for(event.id).points
                        item_form.average = event.average_score
                    else:
                        item_form.score = item_form.average = ''
                else:
                    item_form.winner = item_form.score = item_form.average = ''
                self.winners.append_entry(item_form)

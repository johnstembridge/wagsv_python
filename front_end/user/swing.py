import os
from flask_wtf import FlaskForm
from flask import render_template
from wtforms import StringField, FormField, FieldList

from back_end.calc import get_big_swing
from front_end.form_helpers import render_link
from globals import config


class Swing:

    @staticmethod
    def swing_show(year):
        form = SwingForm()
        form.populate_swing(year)
        return render_template('user/swing.html', form=form, year=int(year), render_link=render_link)


class SwingItemForm(FlaskForm):
    position = StringField(label='Position')
    player = StringField(label='Player')
    course = StringField(label='Course')
    date = StringField(label='Date')
    points_out = StringField(label='Front')
    points_in = StringField(label='Back')
    swing = StringField(label='Swing')


class SwingForm(FlaskForm):
    swing = FieldList(FormField(SwingItemForm))
    year = StringField()
    year_span = StringField()
    image_url = StringField()

    def populate_swing(self, year):
        self.year.data = year
        swings = get_big_swing(year)
        for item in swings.data:
            item_form = SwingItemForm()
            item_form.position = item[swings.column_index('position')]
            item_form.player = item[swings.column_index('player')]
            item_form.course = item[swings.column_index('course')]
            item_form.date = item[swings.column_index('date')]
            item_form.points_out = item[swings.column_index('points_out')]
            item_form.points_in = item[swings.column_index('points_in')]
            item_form.swing = item[swings.column_index('swing')]

            self.swing.append_entry(item_form)
        self.year_span.data = str(int(year)-1) + '/' + year
        self.image_url.data = os.path.join(config.get('locations')['base_url'], 'trophies', 'swing.jpg')

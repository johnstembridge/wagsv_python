from flask_wtf import FlaskForm
from flask import render_template
from wtforms import StringField, FormField, FieldList

from back_end.interface import get_big_swing, get_all_big_swing_winners
from back_end.data_utilities import fmt_date
from front_end.form_helpers import render_link
from globals.config import url_for_html, url_for_user


class Swing:

    @staticmethod
    def swing_show(year):
        form = SwingForm()
        year = form.populate_swing(year)
        return render_template('user/swing.html', form=form, year=int(year), render_link=render_link, url_for_user=url_for_user)


    @staticmethod
    def swing_history():
        form = SwingHistoryForm()
        form.populate()
        return render_template('user/swing_history.html', form=form, render_link=render_link, url_for_user=url_for_user)


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

    def populate_swing(self, year=None):
        year_range, swings = get_big_swing(year)
        year = year_range[1]
        self.year.data = str(year)
        for item in swings.data:
            item_form = SwingItemForm()
            item_form.position = item[swings.column_index('position')]
            item_form.player = item[swings.column_index('player')]
            item_form.course = item[swings.column_index('course')]
            item_form.date = fmt_date(item[swings.column_index('date')])
            item_form.points_out = item[swings.column_index('points_out')]
            item_form.points_in = item[swings.column_index('points_in')]
            item_form.swing = item[swings.column_index('swing')]

            self.swing.append_entry(item_form)
        self.year_span.data = str(year_range[0]) + '/' + str(year_range[1])
        self.image_url.data = url_for_html('pictures', 'trophies', 'swing.jpg')
        return year

class SwingHistoryItemForm(FlaskForm):
    year = StringField(label='year')
    player = StringField(label='Player')
    course = StringField(label='Course')
    date = StringField(label='Date')
    points_out = StringField(label='Front')
    points_in = StringField(label='Back')
    swing = StringField(label='Swing')


class SwingHistoryForm(FlaskForm):
    image_url = StringField()
    swing = FieldList(FormField(SwingHistoryItemForm))

    def populate(self):
        all = get_all_big_swing_winners()
        self.image_url.data = url_for_html('pictures', 'trophies', 'swing.jpg')
        for swing in all.data:
            item_form = SwingHistoryItemForm()
            item_form.year = swing[all.column_index('year')]
            item_form.date = swing[all.column_index('date')]
            item_form.player = swing[all.column_index('player')]
            item_form.course = swing[all.column_index('course')]
            item_form.points_out = swing[all.column_index('points_out')]
            item_form.points_in = swing[all.column_index('points_in')]
            item_form.swing = swing[all.column_index('swing')]
            self.swing.append_entry(item_form)


from flask_wtf import FlaskForm
from flask import render_template
from wtforms import StringField, FormField, FieldList

from back_end.interface import get_all_holes_in_one
from back_end.data_utilities import fmt_date
from front_end.form_helpers import render_link


class HoleInOne:

    @staticmethod
    def history():
        form = HoleInOneHistoryForm()
        form.populate()
        return render_template('user/hole_in_one_history.html', form=form, render_link=render_link)


class HoleInOneHistoryItemForm(FlaskForm):
    player = StringField(label='Player')
    date = StringField(label='Date')
    course = StringField(label='Course')
    hole = StringField(label='Hole')

class HoleInOneHistoryForm(FlaskForm):
    hist = FieldList(FormField(HoleInOneHistoryItemForm))

    def populate(self):
        all = get_all_holes_in_one()
        for (date, player, course, hole) in all:
            item_form = HoleInOneHistoryItemForm()
            item_form.player = player
            item_form.date = fmt_date(date)
            item_form.course = course
            item_form.hole = hole
            self.hist.append_entry(item_form)


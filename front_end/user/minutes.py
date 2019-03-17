from flask import render_template, redirect, flash
from flask_wtf import FlaskForm
from wtforms import StringField, FieldList, FormField, SubmitField, SelectField, HiddenField

from globals.enumerations import MinutesType
from back_end.data_utilities import fmt_date, parse_date
from back_end.interface import get_all_years
from front_end.form_helpers import render_link
from globals.config import url_for_user
from models.minutes import Minutes


class MinutesShow:
    @staticmethod
    def minutes_show():
        form = MinutesShowForm()
        if form.is_submitted():
            minutes = form.populate()
            if minutes:
                return redirect(minutes.file_link())
        return render_template('user/minutes_show.html', form=form, render_link=render_link, url_for_user=url_for_user)


class MinutesShowItemForm(FlaskForm):
    mtype = StringField(label='Type')
    mdate = StringField(label='Date')
    mlink = StringField(label='Link')


class MinutesShowForm(FlaskForm):
    minutes_year = SelectField(label='Year', choices=[(str(y), str(y)) for y in ['all'] + get_all_years()])
    minutes_type = SelectField(label='Meeting type', choices=MinutesType.choices(), coerce=MinutesType.coerce)
    select = SubmitField(label='Select')
    type_year = HiddenField()
    choices = FieldList(FormField(MinutesShowItemForm))

    def populate(self):
        type = self.minutes_type.data
        year = self.minutes_year.data
        type_year = type.name + '_' + year
        type = None if type.name == 'all' else type
        year = None if year == 'all' else int(year)
        minutes = Minutes.get_all_minutes(type, year)
        if len(minutes) == 0:
            flash('None found', 'warning')
        if len(minutes) == 1:
            return minutes[0]
        for m in minutes:
            item_form = MinutesShowItemForm()
            item_form.mtype = m.full_type()
            item_form.mdate = fmt_date(m.date)
            item_form.mlink = m.file_link()
            self.choices.append_entry(item_form)

        return None

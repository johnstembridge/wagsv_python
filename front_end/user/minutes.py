from flask import render_template, redirect
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, HiddenField

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


class MinutesShowForm(FlaskForm):
    minutes_type = SelectField(label='Meeting type', choices=MinutesType.choices(), coerce=MinutesType.coerce)
    minutes_year = SelectField(label='Year', choices=[(str(y), str(y)) for y in get_all_years()])
    minutes = SelectField(label='Minutes', choices=[])
    select = SubmitField(label='Select')
    type_year = HiddenField()

    def populate(self):
        type_year = self.minutes_type.data.name + '_' + self.minutes_year.data
        if type_year != self.type_year.data:
            minutes = Minutes.get_all_minutes(self.minutes_type.data, int(self.minutes_year.data))
            if len(minutes) == 1:
                return minutes[0]
            choices = [fmt_date(m.date) for m in minutes]
            self.minutes.choices = list(zip(choices, choices))
        if self.minutes.data is not None and self.minutes.data != 'None' and type_year == self.type_year.data:
            return Minutes.get_minutes(self.minutes_type.data, parse_date(self.minutes.data))
        else:
            self.type_year.data = type_year
            return None

from flask_wtf import FlaskForm
from flask import render_template, session
from wtforms import SubmitField, SelectField
from interface import get_all_years, create_events_file
from form_helpers import set_select_field


def home_main(year):
    form = HomeForm()
    if form.is_submitted():
        year = form.new_year.data
        if form.save(year):
            session['current_year'] = year
    form.populate(year)
    return render_template('home.html', form=form, year=year)


def page_not_found(e):
    return render_template('404.html'), 404


class HomeForm(FlaskForm):
    new_year = SelectField(label='Change year')
    submit = SubmitField(label='Save')

    def populate(self, year):
        set_select_field(self.new_year, 'year', get_all_years(), year)

    def save(self, year):
        # create directory and files if necessary
        return create_events_file(year)

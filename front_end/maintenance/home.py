from flask_wtf import FlaskForm
from flask import render_template, session, make_response
from wtforms import SubmitField, SelectField
from interface import get_all_years


def home_main(year):
    form = HomeForm()
    if form.is_submitted():
        year = form.new_year.data
        response = make_response(render_template('home.html', form=form, year=year))
        session['current_year'] = year
        return response
    if not form.is_submitted():
        form.populate(year)
    return render_template('home.html', form=form, year=year)


def page_not_found(e):
    return render_template('404.html'), 404


class HomeForm(FlaskForm):
    new_year = SelectField(label='Change year', choices=[('', 'Choose year ...')] + get_all_years())
    submit = SubmitField(label='Save')

    def populate(self, year):
        self.new_year.default = year

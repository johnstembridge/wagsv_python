from flask_wtf import FlaskForm
from flask import render_template, flash
from wtforms import StringField


def home_main(year):
    form = HomeForm()
    form.populate(year)
    return render_template('home.html', form=form, year=year)


def page_not_found(e):
    return render_template('404.html'), 404


class HomeForm(FlaskForm):
    year = StringField(label='Year')

    def populate(self, year):
        pass

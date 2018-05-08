import datetime

from flask_login import login_required, LoginManager
from flask_wtf import FlaskForm
from flask import render_template, session
from wtforms import SubmitField, SelectField
from wags_admin import app
from back_end.interface import get_all_years, create_events_file
from front_end.form_helpers import set_select_field
from globals import config

login_manager = LoginManager(app)
login_manager.login_view = config.get('url_prefix')['admin']+'/login'


@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
@login_required
def index():
    current_year = get_user_current_year()
    return home_main(current_year)


def home_main(year):
    form = HomeForm()
    if form.is_submitted():
        year = form.new_year.data
        if form.save(year):
            session['current_year'] = year
    form.populate(year)
    return render_template('admin/home.html', form=form, year=year)


def page_not_found(e):
    return render_template('admin/404.html'), 404


def internal_error(e):
    return render_template('admin/500.html'), 500


def get_user_current_year():
    if 'current_year' in session:
        current_year = session['current_year']
    else:
        current_year = datetime.date.today().year
        session['current_year'] = current_year
    return current_year


class HomeForm(FlaskForm):
    new_year = SelectField(label='Change year')
    submit = SubmitField(label='Save')

    def populate(self, year):
        set_select_field(self.new_year, 'year', get_all_years(), year)

    def save(self, year):
        # create directory and files if necessary
        return create_events_file(year)

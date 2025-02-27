from flask_login import login_required
from flask_wtf import FlaskForm
from flask import render_template, flash
from wtforms import SubmitField, SelectField
from wags_admin import app
from back_end.interface import get_all_years, create_events_file
from front_end.form_helpers import set_select_field
from front_end.admin.others import get_user_current_year, set_user_current_year
from globals.decorators import role_required


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def index():
    current_year = get_user_current_year()
    return home_main(current_year)


@app.route('/<int:year>', methods=['GET', 'POST'])
@app.route('/index/int:<year>')
@login_required
@role_required('admin')
def index_for_year(year):
    set_user_current_year(year)
    return home_main(year)


def home_main(year):
    form = HomeForm()
    if form.is_submitted():
        year = int(form.new_year.data)
        if form.save(year):
            flash('Current year changed to {}'.format(year), 'success')
    form.populate(year)
    form.new_year.data = year # have to set default value for selectfield here
    return render_template('admin/home.html', form=form, year=year)


class HomeForm(FlaskForm):
    new_year = SelectField(label='Change current year to', coerce=int)
    submit = SubmitField(label='Change')

    def populate(self, year):
        set_select_field(self.new_year, get_all_years(), 'year')

    def save(self, year):
        if year != get_user_current_year():
            set_user_current_year(year)
            # create directory and files if necessary
            create_events_file(year)
            return True
        else:
            return False

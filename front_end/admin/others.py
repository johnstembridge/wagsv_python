import datetime
from flask import render_template, session


def unauthorised(e):
    return render_template('admin/401.html'), 404


def page_not_found(e):
    return render_template('admin/404.html'), 404


def internal_error(e):
    return render_template('admin/500.html'), 500


def get_user_current_year():
    if 'current_year' in session:
        current_year = session['current_year']
        if isinstance(current_year, int):
            return current_year
    current_year = datetime.date.today().year
    session['current_year'] = current_year
    return current_year


def set_user_current_year(year):
    session['current_year'] = year


def reset_user_current_year():
    if 'current_year' in session:
        session.pop('current_year')

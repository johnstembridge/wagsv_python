import datetime
from flask import render_template, session


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

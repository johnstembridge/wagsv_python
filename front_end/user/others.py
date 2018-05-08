from flask import render_template


def page_not_found(e):
    return render_template('user/404.html'), 404


def internal_error(e):
    return render_template('user/500.html'), 500

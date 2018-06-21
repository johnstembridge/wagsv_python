from flask import Flask

from globals.app_setup import init_app
from front_end.admin.others import page_not_found, internal_error, unauthorised

app = Flask(__name__)
db = init_app(app)

from views.admin.access import *
from front_end.admin.home import *
from views.admin.accounts import *
from views.admin.events import *
from views.admin.members import *
from views.admin.news import *
from views.admin.venues import *


@app.errorhandler(401)
def not_found(e):
    return unauthorised(e)


@app.errorhandler(404)
def not_found(e):
    return page_not_found(e)


@app.errorhandler(500)
def catch_internal_error(e):
    app.logger.error(e)
    return internal_error(e)


@app.context_processor
def override_url_for():
    return dict(url_for=config.url_for_admin)


if __name__ == '__main__':
    app.run(debug=False)

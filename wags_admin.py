from flask import Flask
from flask_bootstrap import Bootstrap
from flask_wtf import CSRFProtect

from globals import logging
from globals.db_setup import init_db

app = Flask(__name__)

db = init_db(app)

bootstrap = Bootstrap(app)
csrf = CSRFProtect(app)
log_handler = logging.log_init()
app.logger.addHandler(log_handler)

from front_end.admin.home import *
from views.admin.access import *
from views.admin.accounts import *
from views.admin.events import *
from views.admin.members import *
from views.admin.news import *
from views.admin.venues import *


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

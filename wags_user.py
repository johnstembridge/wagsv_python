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

from views.user.events import *
from views.user.players import *
from views.user.others import *
from front_end.user.others import page_not_found, internal_error


@app.errorhandler(404)
def not_found(e):
    return page_not_found(e)


@app.errorhandler(500)
def catch_internal_error(e):
    app.logger.error(e)
    return internal_error(e)


if __name__ == '__main__':
    app.run(debug=True)

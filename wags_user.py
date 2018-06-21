from flask import Flask

from globals.app_setup import init_app

app = Flask(__name__)
#db = init_app(app, create=True)
db = init_app(app)

from views.user.access import *
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
    app.run(debug=False)

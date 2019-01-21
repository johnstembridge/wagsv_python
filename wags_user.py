from flask import Flask

from globals.app_setup import init_app


def _force_https(app):
    def wrapper(environ, start_response):
        environ['wsgi.url_scheme'] = 'https'
        return app(environ, start_response)
    return wrapper


app = Flask(__name__)
app = _force_https(app)
#init_app(app, create=True)
init_app(app)

from views.user.access import *
from views.user.events import *
from views.user.players import *
from views.user.members import *
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
    #app.run(host="0.0.0.0", port=8100, debug=False)
    app.run(debug=False)

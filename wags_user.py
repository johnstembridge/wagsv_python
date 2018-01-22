import datetime

from flask import Flask, request, session
from flask_bootstrap import Bootstrap
from front_end.user.events_user import ReportEvents

from globals import config, logging

app = Flask(__name__)
app.config['SECRET_KEY'] = config.get('SECRET_KEY')
bootstrap = Bootstrap(app)
log_handler = logging.log_init()
app.logger.addHandler(log_handler)


@app.route('/', methods=['GET', 'POST'])
def index():
    current_year = get_user_current_year()
    return events_list_events(current_year)


# region events
@app.route('/events/<year>', methods=['GET', 'POST'])
def events_list_events(year):
    return ReportEvents.list_events(year)


@app.route('/events/<year>/<event_id>/book', methods=['GET', 'POST'])
def book_event(year, event_id):
    event_type = request.args.get('event_type')
    return ReportEvents.book_event(year, event_id, event_type)


@app.route('/events/<year>/<event_id>/show', methods=['GET', 'POST'])
def show_event(year, event_id):
    event_type = request.args.get('event_type')
    return ReportEvents.show_event(year, event_id, event_type)


@app.route('/events/<year>/<event_id>/results', methods=['GET', 'POST'])
def results_event(year, event_id):
    event_type = request.args.get('event_type')
    return ReportEvents.results_event(year, event_id, event_type)


@app.route('/events/<year>/<event_id>/report', methods=['GET', 'POST'])
def report_event(year, event_id):
    event_type = request.args.get('event_type')
    return ReportEvents.report_event(year, event_id, event_type)


@app.route('/events/<year>/<event_id>/<player_id>/card', methods=['GET', 'POST'])
def card_event_player(year, event_id, player_id):
    return ReportEvents.card_event_player(year, event_id, player_id)


@app.route('/events/<year>/<event_id>/<player_id>/handicap', methods=['GET', 'POST'])
def handicap_history_player(year, event_id, player_id):
    return ReportEvents.handicap_history_player(year, event_id, player_id)
# endregion


@app.errorhandler(404)
def not_found(e):
    return ReportEvents.page_not_found(e)


@app.errorhandler(500)
def catch_internal_error(e):
    app.logger.error(e)
    return ReportEvents.internal_error(e)


@app.context_processor
def override_url_for():
    return dict(url_for=config.url_for_user)


def get_user_current_year():
    if 'current_year' in session:
        current_year = session['current_year']
    else:
        current_year = datetime.date.today().year
        session['current_year'] = current_year
    return current_year


if __name__ == '__main__':
    app.run(debug=False)
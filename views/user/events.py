import datetime

from flask import request
from wags_user import app
from front_end.user.events import ReportEvents


@app.route('/', methods=['GET', 'POST'])
def index():
    current_year = datetime.date.today().year
    return list_events(current_year)


@app.route('/events', methods=['GET', 'POST'])
def events():
    # replacement end point for old-style non-restful service event calls
    # e.g. http://wags.org/wagsuser/events?date=2017/11/18&event=Pine%20Ridge
    if request.args is not None and len(request.args) > 0:
        return ReportEvents.show_from_date_and_name(request.args['date'], request.args['event'])
    else:
        return ReportEvents.select_event()


@app.route('/events/<year>', methods=['GET', 'POST'])
def list_events(year):
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


@app.route('/events/<date>/results', methods=['GET', 'POST'])
def results_event_date(date):
    date = date.replace('-', '/')
    return ReportEvents.results_event_date(date)


@app.route('/events/<year>/<event_id>/report', methods=['GET', 'POST'])
def report_event(year, event_id):
    event_type = request.args.get('event_type')
    return ReportEvents.report_event(year, event_id, event_type)


@app.route('/events/<date>/<player_id>/card', methods=['GET', 'POST'])
def card_event_player(date, player_id):
    date = date.replace('-', '/')
    return ReportEvents.card_event_player(date, player_id)


@app.route('/events/<year>/<event_id>/<player_id>/handicap', methods=['GET', 'POST'])
def event_handicap_history_player(year, event_id, player_id):
    return ReportEvents.handicap_history_player(year, event_id, player_id)


import datetime

from flask import Flask, request, session
from flask_bootstrap import Bootstrap
from front_end.user.events_user import ReportEvents
from front_end.user.handicaps import Handicaps
from front_end.user.vl import Vl

from globals import config, logging
from front_end.user.swing import Swing

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
@app.route('/events', methods=['GET', 'POST'])
def events():
    # replacement end point for old-style non-restful service event calls
    # e.g. http://wags.org/wagsuser/events?date=2017/11/18&event=Pine%20Ridge
    if request.args is not None and len(request.args) > 0:
        return ReportEvents.show_from_date_and_name(request.args['date'], request.args['event'])
    else:
        current_year = get_user_current_year()
        return events_list_events(current_year)


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
def event_handicap_history_player(year, event_id, player_id):
    return ReportEvents.handicap_history_player(year, event_id, player_id)
# endregion


# region handicaps
@app.route('/handicaps', methods=['GET', 'POST'])
def handicaps():
    return Handicaps.list_handicaps()


@app.route('/handicaps/<player_id>', methods=['GET', 'POST'])
def handicap_history_player(player_id):
    return Handicaps.handicap_history_player(player_id)
# endregion


@app.route('/vl/<year>', methods=['GET', 'POST'])
def vl(year):
    return Vl.vl_show(year)


@app.route('/swing/<year>', methods=['GET', 'POST'])
def swing(year):
    return Swing.swing_show(year)


@app.route('/players/<player_id>/<year>', methods=['GET', 'POST'])
def show_player_events_for_year(player_id, year):
    return ReportEvents.show_playing_history(player_id, year)


@app.route('/players/<player_id>', methods=['GET', 'POST'])
def show_player_events(player_id):
    return ReportEvents.show_playing_history(player_id)


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

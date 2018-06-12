import datetime

from flask_login import login_required, LoginManager, current_user
from wags_user import app
from front_end.user.events import ReportEvents

from globals import config

login_manager = LoginManager(app)
login_manager.login_view = config.get('url_prefix')['user']+'/login'


@app.route('/', methods=['GET', 'POST'])
def index():
    current_year = datetime.date.today().year
    return list_events(current_year)


@app.route('/events', methods=['GET', 'POST'])
@login_required
def events():
    return ReportEvents.select_event()


@app.route('/events/<year>', methods=['GET', 'POST'])
@login_required
def list_events(year):
    return ReportEvents.list_events(year)


@app.route('/events/<event_id>/book', methods=['GET', 'POST'])
@login_required
def book_event(event_id):
    member_id = current_user.member_id
    return ReportEvents.show_or_book_event(int(event_id), member_id)


@app.route('/events/<event_id>/show', methods=['GET', 'POST'])
@login_required
def show_event(event_id):
    member_id = current_user.member_id
    return ReportEvents.show_or_book_event(int(event_id), member_id)


@app.route('/events/<event_id>/show_all', methods=['GET', 'POST'])
@login_required
def show_all_bookings(event_id):
    return ReportEvents.show_all_bookings(event_id)


@app.route('/events/<event_id>/results', methods=['GET', 'POST'])
@login_required
def results_event(event_id):
    return ReportEvents.results_event(int(event_id))


@app.route('/events/<event_id>/report', methods=['GET', 'POST'])
@login_required
def report_event(event_id):
    return ReportEvents.report_event(int(event_id))


@app.route('/events/<event_id>/<player_id>/card', methods=['GET', 'POST'])
@login_required
def card_event_player(event_id, player_id):
    return ReportEvents.card_event_player(int(event_id), int(player_id))



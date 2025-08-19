from flask_login import login_required, current_user
from wags_user import app
from front_end.user.events import ReportEvents

from back_end.data_utilities import current_year


@app.route('/events/cards', methods=['GET', 'POST'])
@login_required
def list_fixture_cards():
    return ReportEvents.list_fixture_cards()


@app.route('/', methods=['GET', 'POST'])
def index():
    return list_events(current_year())


@app.route('/events', methods=['GET', 'POST'])
def list_events_():
    return list_events(current_year())


@app.route('/events/<int:year>', methods=['GET', 'POST'])
def list_events(year):
    return ReportEvents.list_events(year)


@app.route('/events/<int:event_id>/book', methods=['GET', 'POST'])
@login_required
def book_event(event_id):
    member_id = current_user.member_id
    return ReportEvents.show_or_book_event(event_id, member_id)


@app.route('/events/<int:event_id>/show', methods=['GET', 'POST'])
@login_required
def show_event(event_id):
    member_id = current_user.member_id
    return ReportEvents.show_or_book_event(event_id, member_id)


@app.route('/events/<int:event_id>/show_all', methods=['GET', 'POST'])
@login_required
def show_all_bookings(event_id):
    return ReportEvents.show_all_bookings(event_id)


@app.route('/events/<int:event_id>/results', methods=['GET', 'POST'])
@login_required
def results_event(event_id):
    return ReportEvents.results_event(event_id)


@app.route('/events/<int:event_id>/report', methods=['GET', 'POST'])
@login_required
def report_event(event_id):
    return ReportEvents.report_event(event_id)


@app.route('/events/<int:event_id>/<int:player_id>/card', methods=['GET', 'POST'])
@login_required
def card_event_player(event_id, player_id):
    return ReportEvents.card_event_player(event_id, player_id)

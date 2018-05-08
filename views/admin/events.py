from flask import request
from wags_admin import app
from front_end.admin.events_admin import MaintainEvents
from front_end.admin.home import get_user_current_year


@app.route('/events', methods=['GET', 'POST'])
def events_main():
    current_year = get_user_current_year()
    return MaintainEvents.list_events(current_year)


@app.route('/events/<year>', methods=['GET', 'POST'])
def list_events(year):
    return MaintainEvents.list_events(year)


@app.route('/events/<year>/<event_id>', methods=['GET', 'POST'])
def edit_event(year, event_id):
    event_type = request.args.get('event_type')
    return MaintainEvents.edit_event(year, event_id, event_type)


@app.route('/events/<year>/<event_id>/results', methods=['GET', 'POST'])
def results_event(year, event_id):
    event_type = request.args.get('event_type')
    return MaintainEvents.results_event(year, event_id, event_type)


@app.route('/events/<year>/<event_id>/<player_id>/card', methods=['GET', 'POST'])
def card_event_player(year, event_id, player_id):
    position = request.args.get('position')
    handicap = request.args.get('handicap')
    status = request.args.get('status')
    return MaintainEvents.card_event_player(year, event_id, player_id, position, handicap, status)


@app.route('/events/<year>/<event_id>/report', methods=['GET', 'POST'])
def report_event(year, event_id):
    event_type = request.args.get('event_type')
    return MaintainEvents.report_event(year, event_id, event_type)


@app.route('/events/<year>/<event_id>/handicaps', methods=['GET', 'POST'])
def handicaps_event(year, event_id):
    return MaintainEvents.handicaps_event(year, event_id)


@app.route('/events/<year>/<event_id>/<player_id>/handicap', methods=['GET', 'POST'])
def event_handicap_history_player(year, event_id, player_id):
    return MaintainEvents.handicap_history_player(year, event_id, player_id)

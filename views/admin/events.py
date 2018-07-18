from flask import request
from flask_login import login_required, current_user

from back_end.interface import get_event
from front_end.user.events import ReportEvents
from globals.decorators import role_required
from globals.enumerations import EventType
from wags_admin import app
from front_end.admin.events_admin import MaintainEvents
from front_end.admin.others import get_user_current_year


@app.route('/events', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def events_main():
    current_year = get_user_current_year()
    return MaintainEvents.list_events(current_year)


@app.route('/events/<year>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def list_events(year):
    return MaintainEvents.list_events(year)


@app.route('/events/<event_id>/details', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_event(event_id):
    event_type = request.args.get('event_type')
    event_type = EventType(int(request.args.get('event_type'))) if event_type else None  # for add event/tour
    return MaintainEvents.edit_event(int(event_id), event_type)


@app.route('/events/<event_id>/results', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def results_event(event_id):
    event_id = int(event_id)
    event_type = get_event(event_id).type
    if event_type == EventType.wags_vl_event:
        return MaintainEvents.results_vl_event(event_id)
    else:
        return ReportEvents.results_tour_event(event_id)


@app.route('/events/<event_id>/add_player', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_player_to_event(event_id):
    member_id = current_user.member_id
    return MaintainEvents.add_player_to_event(int(event_id), member_id)


@app.route('/events/<event_id>/<player_id>/card', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def card_event_player(event_id, player_id):
    position = request.args.get('position')
    handicap = request.args.get('handicap')
    status = request.args.get('status')
    return MaintainEvents.card_event_player(event_id, player_id, position, handicap, status)


@app.route('/events/<event_id>/report', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def report_event(event_id):
    return MaintainEvents.report_event(event_id)


@app.route('/events/<event_id>/handicaps', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def handicaps_event(event_id):
    return MaintainEvents.handicaps_event(event_id)


@app.route('/events/<event_id>/<player_id>/handicap', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def event_handicap_history_player(event_id, player_id):
    return MaintainEvents.handicap_history_player(event_id, player_id)


@app.route('/trophies/<trophy_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def trophy(trophy_id):
    pass
    #return Trophy.trophy_show(int(trophy_id))

import datetime

from flask import Flask, request, session
from flask_bootstrap import Bootstrap
from flask_wtf import CSRFProtect

from front_end import accounts_admin
from front_end.events_admin import MaintainEvents
from globals import config
from front_end.home import home_main, page_not_found
from front_end.venues_admin import MaintainVenues

app = Flask(__name__)
app.config['SECRET_KEY'] = config.get('SECRET_KEY')
csrf = CSRFProtect(app)
bootstrap = Bootstrap(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    current_year = get_user_current_year()
    return home_main(current_year)


@app.route('/accounts', methods=['GET', 'POST'])
def accounts_main():
    current_year = get_user_current_year()
    return accounts_admin.upload_file(current_year)


@app.route('/accounts/<year>/upload', methods=['GET', 'POST'])
def accounts_upload_file(year):
    return accounts_admin.upload_file(year)


@app.route('/venues', methods=['GET', 'POST'])
def venues_main():
    return MaintainVenues.list_venues()


@app.route('/venues/<venue_id>', methods=['GET', 'POST'])
def edit_venue(venue_id):
    return MaintainVenues.edit_venue(venue_id)


@app.route('/venues/<venue_id>/courses/<course_id>', methods=['GET', 'POST'])
def edit_course(venue_id, course_id):
    return MaintainVenues.edit_course(venue_id, course_id)


# region Events
@app.route('/events', methods=['GET', 'POST'])
def events_main():
    current_year = get_user_current_year()
    return MaintainEvents.list_events(current_year)


@app.route('/events/<year>', methods=['GET', 'POST'])
def events_list_events(year):
    return MaintainEvents.list_events(year)


@app.route('/events/<year>/<event_id>', methods=['GET', 'POST'])
def edit_event(year, event_id):
    event_type = request.args.get('event_type')
    return MaintainEvents.edit_event(year, event_id, event_type)


@app.route('/events/<year>/<event_id>/results', methods=['GET', 'POST'])
def results_event(year, event_id):
    event_type = request.args.get('event_type')
    return MaintainEvents.results_event(year, event_id, event_type)


@app.route('/events/<year>/<event_id>/handicaps', methods=['GET', 'POST'])
def handicaps_event(year, event_id):
    return MaintainEvents.handicaps_event(year, event_id)


@app.route('/events/<year>/<event_id>/<player_id>/card', methods=['GET', 'POST'])
def card_event_player(year, event_id, player_id):
    return MaintainEvents.card_event_player(year, event_id, player_id)


@app.route('/events/<year>/<event_id>/<player_id>/handicap', methods=['GET', 'POST'])
def handicap_history_player(year, event_id, player_id):
    return MaintainEvents.handicap_history_player(year, event_id, player_id)
# endregion


@app.errorhandler(404)
def not_found(e):
    return page_not_found(e)


def get_user_current_year():
    if 'current_year' in session:
        current_year = session['current_year']
    else:
        current_year = datetime.date.today().year
        session['current_year'] = current_year
    return current_year


if __name__ == '__main__':
    app.run(debug=True)
import datetime

from flask import Flask, request, session
from flask_bootstrap import Bootstrap
from flask_wtf import CSRFProtect
from flask_login import LoginManager, login_required

from front_end.admin.news_admin import MaintainNews
from front_end.admin.events_admin import MaintainEvents
from front_end.admin.members_admin import MaintainMembers
from front_end.admin.venues_admin import MaintainVenues
from front_end.admin import accounts_admin
from front_end.admin import login
from front_end.admin.home import home_main, page_not_found, internal_error
from globals import config, logging
from models.user import User


app = Flask(__name__)

login_manager = LoginManager(app)
login_manager.login_view = config.get('url_prefix')['admin']+'/login'

app.config['SECRET_KEY'] = config.get('SECRET_KEY')
csrf = CSRFProtect(app)
bootstrap = Bootstrap(app)
log_handler = logging.log_init()
app.logger.addHandler(log_handler)


# region Access
@login_manager.user_loader
def load_user(id):
    return User.get(id=int(id))


@app.route('/login', methods=['GET', 'POST'])
def admin_login():
    next_page = request.args.get('next')
    return login.admin_login(next_page)


@app.route('/register', methods=['GET', 'POST'])
def admin_register():
    return login.admin_register()
# endregion


@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
@login_required
def index():
    current_year = get_user_current_year()
    return home_main(current_year)


# region accounts
@login_required
@app.route('/accounts', methods=['GET', 'POST'])
def accounts_main():
    current_year = get_user_current_year()
    return accounts_admin.upload_file(current_year)


@app.route('/accounts/<year>/upload', methods=['GET', 'POST'])
def accounts_upload_file(year):
    return accounts_admin.upload_file(year)
# endregion


# region venues
@app.route('/venues', methods=['GET', 'POST'])
@login_required
def venues_main():
    return MaintainVenues.list_venues()


@app.route('/venues/<venue_id>', methods=['GET', 'POST'])
def edit_venue(venue_id):
    return MaintainVenues.edit_venue(venue_id)


@app.route('/venues/<venue_id>/courses/<course_id>', methods=['GET', 'POST'])
def edit_course(venue_id, course_id):
    return MaintainVenues.edit_course(venue_id, course_id)
# endregion


# region members
@app.route('/members', methods=['GET', 'POST'])
@login_required
def members_main():
    return MaintainMembers.list_members()


@app.route('/members/<member_id>', methods=['GET', 'POST'])
def edit_member(member_id):
    return MaintainMembers.edit_member(member_id)
# endregion


# region events
@app.route('/events', methods=['GET', 'POST'])
@login_required
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
# endregion


# region news
@app.route('/news', methods=['GET', 'POST'])
@login_required
def news_main():
    return MaintainNews.list_news()


@app.route('/news/<news_date>', methods=['GET', 'POST'])
def edit_news(news_date):
    return MaintainNews.edit_news(news_date)
# endregion


@app.errorhandler(404)
def not_found(e):
    return page_not_found(e)


@app.errorhandler(500)
def catch_internal_error(e):
    app.logger.error(e)
    return internal_error(e)


@app.context_processor
def override_url_for():
    return dict(url_for=config.url_for_admin)


def get_user_current_year():
    if 'current_year' in session:
        current_year = session['current_year']
    else:
        current_year = datetime.date.today().year
        session['current_year'] = current_year
    return current_year


if __name__ == '__main__':
    app.run(debug=False)

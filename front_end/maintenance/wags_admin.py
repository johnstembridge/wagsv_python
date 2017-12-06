from flask import Flask
from flask_wtf import CSRFProtect
from flask_bootstrap import Bootstrap
import config
import accounts
from events import MaintainEvents

app = Flask(__name__)
app.config['SECRET_KEY'] = config.get('SECRET_KEY')
csrf = CSRFProtect(app)

bootstrap = Bootstrap(app)


@app.route('/')
def index():
    return '<h1>Hi!</h1'


@app.route('/accounts/<year>/upload', methods=['GET', 'POST'])
def accounts_upload_file(year):
    return accounts.upload_file(year)


@app.route('/events', methods=['GET', 'POST'])
def events_main():
    return MaintainEvents.list_events('2017')


@app.route('/events/<year>', methods=['GET', 'POST'])
def events_list_events(year):
    return MaintainEvents.list_events(year)


@app.route('/events/<year>/<event_id>', methods=['GET', 'POST'])
def edit_event(year, event_id):
    return MaintainEvents.edit_event(year, event_id)


@app.route('/events/<year>/<event_id>/results', methods=['GET', 'POST'])
def results_event(year, event_id):
    return MaintainEvents.results_event(year, event_id)


@app.route('/events/<year>/<event_id>/handicaps', methods=['GET', 'POST'])
def handicaps_event(year, event_id):
    return MaintainEvents.handicaps_event(year, event_id)


@app.route('/events/<year>/<event_id>/<player_id>/card', methods=['GET', 'POST'])
def card_event_player(year, event_id, player_id):
    return MaintainEvents.card_event_player(year, event_id, player_id)


@app.route('/events/<year>/<event_id>/<player_id>/handicap', methods=['GET', 'POST'])
def handicap_history_player(year, event_id, player_id):
    return MaintainEvents.handicap_history_player(year, event_id, player_id)


# @staticmethod
# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
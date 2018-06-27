from wags_user import app, login_required
from front_end.user.players import ReportPlayers


@app.route('/players/summary', methods=['GET', 'POST'])
@login_required
def summary():
    return ReportPlayers.playing_history_summary()


@app.route('/players/<player_id>', methods=['GET', 'POST'])
@login_required
def show_player_events(player_id):
    return ReportPlayers.playing_history_player(int(player_id))


@app.route('/players/<player_id>/<year>', methods=['GET', 'POST'])
@login_required
def show_player_events_for_year(player_id, year):
    return ReportPlayers.playing_history_player(int(player_id), int(year))

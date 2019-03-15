from wags_user import app, login_required
from front_end.user.handicaps import Handicaps
from front_end.user.trophy import Trophy
from front_end.user.vl import Vl
from front_end.user.swing import Swing
from front_end.user.minutes import MinutesShow

from back_end.data_utilities import current_year, coerce


# region handicaps
@app.route('/handicaps', methods=['GET', 'POST'])
@login_required
def handicaps():
    return Handicaps.list_handicaps()


@app.route('/handicaps/<player_id>', methods=['GET', 'POST'])
@login_required
def handicap_history_player(player_id):
    return Handicaps.handicap_history_player(int(player_id))
# endregion


# region reports
@app.route('/vl', methods=['GET', 'POST'])
@login_required
def vl_():
    return vl(current_year())


@app.route('/vl/<year>', methods=['GET', 'POST'])
@login_required
def vl(year):
    return Vl.vl_show(coerce(year, int))


@app.route('/swing', methods=['GET', 'POST'])
@login_required
def swing_():
    return swing(current_year())


@app.route('/swing/<year>', methods=['GET', 'POST'])
@login_required
def swing(year):
    return Swing.swing_show(coerce(year, int))


@app.route('/trophies/<trophy_id>', methods=['GET', 'POST'])
@login_required
def trophy_history(trophy_id):
    return Trophy.trophy_show(int(trophy_id))
# endregion


@app.route("/minutes", methods=['GET', 'POST'])
def show_minutes():
    return MinutesShow.minutes_show()


@app.route("/log")
def log_test():
    app.logger.warning('testing warning log')
    app.logger.error('testing error log')
    app.logger.info('testing info log')
    return "Log testing"

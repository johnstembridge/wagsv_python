from wags_user import app, login_required
from front_end.user.handicaps import Handicaps
from front_end.user.trophy import Trophy
from front_end.user.vl import Vl
from front_end.user.swing import Swing
from front_end.user.minutes import MinutesShow

from back_end.data_utilities import current_year


# region handicaps
@app.route('/handicaps', methods=['GET', 'POST'])
@login_required
def handicaps():
    return Handicaps.list_handicaps()


@app.route('/handicaps/<int:player_id>', methods=['GET', 'POST'])
@login_required
def handicap_history_player(player_id):
    return Handicaps.handicap_history_player(player_id)
# endregion


# region reports
@app.route('/vl', methods=['GET', 'POST'])
@login_required
def vl_():
    return vl(current_year())


@app.route('/vl/<int:year>', methods=['GET', 'POST'])
@login_required
def vl(year):
    return Vl.vl_show(year)


@app.route('/vl_history', methods=['GET', 'POST'])
@login_required
def vl_history():
    return Vl.vl_history()


@app.route('/swing', methods=['GET', 'POST'])
@login_required
def swing_():
    return swing()


@app.route('/swing/<int:year>', methods=['GET', 'POST'])
@login_required
def swing(year=None):
    return Swing.swing_show(year)


@app.route('/swing_history', methods=['GET', 'POST'])
@login_required
def swing_history():
    return Swing.swing_history()


@app.route('/trophies/<int:trophy_id>', methods=['GET', 'POST'])
@login_required
def trophy_history(trophy_id):
    return Trophy.trophy_show(trophy_id)
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

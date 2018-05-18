from wags_user import app
from front_end.user.handicaps import Handicaps
from front_end.user.trophy import Trophy
from front_end.user.vl import Vl
from front_end.user.swing import Swing


# region handicaps
@app.route('/handicaps', methods=['GET', 'POST'])
def handicaps():
    return Handicaps.list_handicaps()


@app.route('/handicaps/<player_id>', methods=['GET', 'POST'])
def handicap_history_player(player_id):
    return Handicaps.handicap_history_player(player_id)
# endregion


# region reports
@app.route('/vl/<year>', methods=['GET', 'POST'])
def vl(year):
    return Vl.vl_show(year)


@app.route('/swing/<year>', methods=['GET', 'POST'])
def swing(year):
    return Swing.swing_show(year)


@app.route('/trophies/<trophy>', methods=['GET', 'POST'])
def trophy(trophy):
    return Trophy.trophy_show(trophy)
# endregion






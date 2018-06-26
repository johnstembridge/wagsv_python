from datetime import datetime
from wags_user import app, current_user
from front_end.user.handicaps import Handicaps
from front_end.user.trophy import Trophy
from front_end.user.vl import Vl
from front_end.user.swing import Swing
from front_end.user.members import Members


# region handicaps
@app.route('/handicaps', methods=['GET', 'POST'])
def handicaps():
    return Handicaps.list_handicaps()


@app.route('/handicaps/<player_id>', methods=['GET', 'POST'])
def handicap_history_player(player_id):
    return Handicaps.handicap_history_player(int(player_id))
# endregion


# region reports
@app.route('/vl/<year>', methods=['GET', 'POST'])
def vl(year):
    return Vl.vl_show(int(year))


@app.route('/swing/<year>', methods=['GET', 'POST'])
def swing(year):
    return Swing.swing_show(year)


@app.route('/trophies/<trophy_id>', methods=['GET', 'POST'])
def trophy(trophy_id):
    return Trophy.trophy_show(int(trophy_id))
# endregion


# region members
@app.route('/members', methods=['GET', 'POST'])
def select_member():
    return Members.select()


@app.route('/members/current', methods=['GET', 'POST'])
def edit_contact_details():
    member_id = current_user.member_id
    return Members.contact(int(member_id), edit=True)


@app.route('/members/<member_id>', methods=['GET', 'POST'])
def show_contact_details(member_id):
    return Members.contact(int(member_id), edit=False)


@app.route('/members/account/<year>', methods=['GET', 'POST'])
def show_member_account(year=None):
    member_id = current_user.member_id
    if year == 'current':
        year = str(datetime.today().year)
    return Members.account(int(member_id), int(year))
# endregion






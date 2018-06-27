from datetime import datetime
from wags_user import app, current_user, login_required
from front_end.user.members import Members


@app.route('/members', methods=['GET', 'POST'])
@login_required
def select_member():
    return Members.select()


@app.route('/members/current', methods=['GET', 'POST'])
@login_required
def edit_contact_details():
    member_id = current_user.member_id
    return Members.contact(int(member_id), edit=True)


@app.route('/members/<member_id>', methods=['GET', 'POST'])
@login_required
def show_contact_details(member_id):
    return Members.contact(int(member_id), edit=False)


@app.route('/members/account/<year>', methods=['GET', 'POST'])
@login_required
def show_member_account(year=None):
    member_id = current_user.member_id
    if year == 'current':
        year = str(datetime.today().year)
    return Members.account(int(member_id), int(year))

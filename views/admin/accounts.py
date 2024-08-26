from flask_login import login_required

from globals.decorators import role_required
from wags_admin import app
from front_end.admin.others import get_user_current_year
from front_end.admin import accounts_admin


@app.route('/accounts/upload', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def accounts_upload_file(year=None):
    if not year:
        year = get_user_current_year()
    return accounts_admin.upload_file(year)


@app.route('/accounts/hio', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def accounts_hole_in_one():
    current_year = get_user_current_year()
    return accounts_admin.hole_in_one(current_year)


@app.route('/accounts/balances', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def accounts_balances(year=None):
    if not year:
        year = get_user_current_year()
    return accounts_admin.accounts_member_balances(year)


@app.route('/members/<member_id>/<year>/account', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def member_account(member_id, year=None):
    if not year:
        year = get_user_current_year()
    return accounts_admin.member_account(member_id, year)

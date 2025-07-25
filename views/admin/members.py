from flask_login import login_required

from globals.decorators import role_required
from wags_admin import app
from front_end.admin.members_admin import MaintainMembers


@app.route('/members/list/current', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def members_list_current():
    return MaintainMembers.list_members('current')


@app.route('/members/list/all', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def members_list_all():
    return MaintainMembers.list_members('all')


@app.route('/members/0', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_new_member():
    return MaintainMembers.edit_member(0, from_form='add')


@app.route('/members/<int:member_id>/current', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_member_current(member_id):
    return MaintainMembers.edit_member(member_id, from_form='current')


@app.route('/members/<int:member_id>/all', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_member_all(member_id):
    return MaintainMembers.edit_member(member_id, from_form='all')

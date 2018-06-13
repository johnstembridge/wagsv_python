from flask_login import login_required

from globals.decorators import role_required
from wags_admin import app
from front_end.admin.members_admin import MaintainMembers


@app.route('/members', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def members_main():
    return MaintainMembers.list_members()


@app.route('/members/<member_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_member(member_id):
    return MaintainMembers.edit_member(int(member_id))

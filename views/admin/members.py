from wags_admin import app
from front_end.admin.members_admin import MaintainMembers


@app.route('/members', methods=['GET', 'POST'])
def members_main():
    return MaintainMembers.list_members()


@app.route('/members/<member_id>', methods=['GET', 'POST'])
def edit_member(member_id):
    return MaintainMembers.edit_member(member_id)

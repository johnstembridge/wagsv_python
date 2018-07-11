from flask_login import login_required, current_user

from globals.decorators import role_required
from wags_admin import app
from front_end.admin import minutes_admin


@app.route('/minutes', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def minutes_main():
    member_id = current_user.member_id
    return minutes_admin.upload_file(member_id)


@app.route('/minutes/upload_minutes', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def minutes_upload_file():
    member_id = current_user.member_id
    return minutes_admin.upload_file(member_id)

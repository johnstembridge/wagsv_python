from flask import render_template, flash
from werkzeug.utils import redirect

from front_end.admin.minutes_admin_form import MinutesAdminForm
from front_end.form_helpers import flash_errors
from globals.config import url_for_admin


def upload_file(member_id):
    form = MinutesAdminForm()
    if form.is_submitted():
        if form.submit.data:
            if form.upload_minutes(member_id):
                flash('Draft minutes uploaded successfully, committee emailed', 'success')
                return redirect(url_for_admin('index'))
        if form.publish.data:
            if form.publish_minutes(member_id):
                flash('Minutes published successfully', 'success')
                return redirect(url_for_admin('index'))
    elif form.errors:
        flash_errors(form)
    if not form.is_submitted():
        form.populate()

    return render_template('admin/minutes_admin.html', form=form)

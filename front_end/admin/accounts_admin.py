from flask import render_template, flash
from .accounts_admin_form import AccountsAdminForm


def upload_file(year):
    form = AccountsAdminForm()
    if form.is_submitted():
        if form.submit_upload.data:
            if form.upload(year):
                flash('file uploaded successfully', 'success')
                # return redirect(url_for_admin('upload_file', year=year))
        if form.submit_hole_in_one.data:
            if form.update_hole_in_one():
                flash('Hole in one fund updated successfully', 'success')
    else:
        form.populate(int(year))

    return render_template('admin/accounts_admin.html', form=form, year=year)

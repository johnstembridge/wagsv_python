from flask import render_template, flash
from .accounts_upload_form import AccountsUploadForm


def upload_file(year):
    form = AccountsUploadForm()
    if form.is_submitted():
        if form.upload(year):
            flash('file uploaded successfully')
            # return redirect(url_for('upload_file', year=year))
    else:
        form.populate(int(year))

    return render_template('admin/accounts_upload.html', form=form, year=year)

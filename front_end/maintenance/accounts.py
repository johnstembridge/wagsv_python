from flask import Flask, render_template, flash
from accounts_upload_form import AccountsUploadForm

app = Flask(__name__)


@app.route('/accounts/<year>/upload', methods=['GET', 'POST'])
def upload_file(year):
    form = AccountsUploadForm()
    if form.is_submitted():
        if form.upload(year):
            flash('file uploaded successfully')
            # return redirect(url_for('upload_file', year=year))
    else:
        form.populate(int(year))

    return render_template('accounts_upload.html', form=form, year=year)

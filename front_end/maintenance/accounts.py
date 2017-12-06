from flask import Flask, render_template, flash
from flask_wtf import CSRFProtect
from flask_bootstrap import Bootstrap
from accounts_upload_form import AccountsUploadForm
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config.get('SECRET_KEY')
csrf = CSRFProtect(app)

bootstrap = Bootstrap(app)


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


if __name__ == '__main__':
    app.run(debug=True)
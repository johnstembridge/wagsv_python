import os

from globals import config
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import FileField, SubmitField


class AccountsUploadForm(FlaskForm):
    fileName = FileField(label='File Name')
    submit = SubmitField(label='Upload')

    def populate(self, year):
        pass

    def upload(self, year):
        filename = secure_filename(self.fileName.data.filename)
        if filename != '':
            file_path = os.path.join(config.get('locations')['data'], year, filename)
            self.fileName.data.save(file_path)
            return True
        else:
            return False

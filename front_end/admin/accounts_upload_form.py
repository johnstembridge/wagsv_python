from flask_wtf.file import FileAllowed
from werkzeug.datastructures import FileStorage

from back_end.data_utilities import html_unescape
from back_end.interface import get_front_page_items, accounts_file
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import FileField, SubmitField


class AccountsUploadForm(FlaskForm):
    file_name = FileField(label='File Name', validators=[FileAllowed(['tab'], 'tab files only!')])
    submit_upload = SubmitField(label='Upload')

    def populate(self, year):
        self.file_name.data = FileStorage(filename='accounts.tab')
        self.hole_in_one.data = html_unescape(get_front_page_items('hole_in_one_fund')['hole_in_one_fund'])

    def upload(self, year):
        filename = secure_filename(self.file_name.data.filename)
        if filename != '':
            file_path = accounts_file(year)
            self.file_name.data.save(file_path)
            return True
        else:
            return False

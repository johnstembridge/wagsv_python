import datetime
import os

from flask_wtf.file import FileAllowed, FileRequired
from werkzeug.datastructures import FileStorage
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, TextAreaField, DateField
from wtforms.validators import InputRequired

from back_end.data_utilities import fmt_date, encode_date
from back_end.interface import get_member, get_committee
from globals import config
from globals.config import url_for_html
from globals.email import send_mail
from models.news import NewsDay, News


class MinutesAdminForm(FlaskForm):
    meeting_date = DateField(label='Meeting date', validators=[InputRequired()])
    file_name = FileField(label='Minutes file name', validators=[FileRequired(), FileAllowed(['pdf'], 'pdf files only!')])
    message = TextAreaField(label='Message (optional)')
    submit = SubmitField(label='Submit')
    publish = SubmitField(label='Publish')

    def populate(self):
        self.meeting_date.data = datetime.date.today()
        self.file_name.data = FileStorage(filename='*.pdf')

    def upload_minutes(self, member_id):
        link = self.save_file(self, draft='drafts')
        # notify committee
        subject = 'Committee meeting {} - draft minutes for review'.format(encode_date(self.meeting_date.data))
        sender = get_member(member_id).contact.email
        message = ['The draft minutes are available here:', link, self.message.data]
        to = [m.member.contact.email for m in get_committee()]
        send_mail(to=to,
                  sender=sender,
                  cc=[],
                  subject='WAGS: ' + subject,
                  message=message)
        return True

    def publish_minutes(self, member_id):
        link = self.save_file(self)
        text = 'Latest committee minutes from ' + get_member(member_id).player.full_name()
        message = self.message.data
        item = (text, link, 'Show minutes')
        news_day = NewsDay(message=message, items=[item])
        News().publish_news_day(news_day)
        return True

    @staticmethod
    def save_file(form, draft=''):
        meeting_date = fmt_date(form.meeting_date.data).replace('/', ' ')
        new_file_name = 'min ' + meeting_date + '.pdf'
        file_path = os.path.join(config.get('locations')['minutes'], draft, new_file_name)
        form.file_name.data.save(file_path)
        link = url_for_html('minutes', draft, new_file_name)
        return link

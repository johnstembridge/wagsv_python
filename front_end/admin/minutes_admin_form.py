import datetime
import os

from flask_wtf.file import FileAllowed, FileRequired
from werkzeug.datastructures import FileStorage
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, TextAreaField, DateField, SelectField
from wtforms.validators import InputRequired

from back_end.data_utilities import fmt_date
from back_end.interface import get_member, get_committee
from globals.email import send_mail
from globals.enumerations import MinutesType
from models.news import NewsDay, News
from models.minutes import Minutes


class MinutesAdminForm(FlaskForm):
    meeting_type = SelectField(label='Meeting type', choices=MinutesType.choices(), coerce=MinutesType.coerce)
    meeting_date = DateField(label='Meeting date', validators=[InputRequired()])
    file_name = FileField(label='Minutes file name', validators=[FileRequired(), FileAllowed(['pdf'], 'pdf files only!')])
    message = TextAreaField(label='Message (optional)')
    submit = SubmitField(label='Submit')
    publish = SubmitField(label='Publish')

    def populate(self):
        self.meeting_date.data = datetime.date.today()
        self.file_name.data = FileStorage(filename='*.pdf')

    def upload_minutes(self, member_id):
        minutes = Minutes(self.meeting_type.data, self.meeting_date.data)
        link = self.save_file(self, minutes, draft=True)
        # notify committee
        subject = '{} {} - draft minutes for review'.format(minutes.full_type(), fmt_date(minutes.date))
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
        minutes = Minutes(self.meeting_type.data, self.meeting_date.data)
        link = self.save_file(self, minutes)
        text = 'Latest {} from {}'.format(minutes.full_type(), get_member(member_id).player.full_name())
        message = self.message.data
        item = (text, link, 'Show minutes')
        news_day = NewsDay(message=message, items=[item])
        News().publish_news_day(news_day)
        return True

    @staticmethod
    def save_file(form, minutes, draft=False):
        new_file_name = minutes.file_name()
        file_path = minutes.file_path(draft)
        link = minutes.file_link(draft)
        form.file_name.data.save(os.path.join(file_path, new_file_name))
        return link

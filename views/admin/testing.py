from flask import render_template
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField

from globals.decorators import role_required
from globals.email import send_mail
from wags_admin import app


@app.route('/test/email', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def test_email():
    subject = 'Test email'
    sender = 'john.stembridge@gmail.com'
    message = 'test message'
    to = [sender]
    send_mail(to=to,
              sender=sender,
              cc=[],
              subject='WAGS: ' + subject,
              message=message)
    form = SendEmailConfirmationForm()
    form.populate(subject, message)
    return render_template('user/event_booking_confirmation.html', form=form)


class SendEmailConfirmationForm(FlaskForm):
    title = StringField(label='Title')
    message = StringField(label='Message')

    def populate(self, title, message):
        self.title.data = title
        self.message.data = message

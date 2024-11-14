from flask import render_template
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField

from globals.decorators import role_required
from globals.email import send_mail, use_sendmail
from wags_admin import app
from front_end.admin import test_email_form

@app.route('/test/email', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def test_email():
    #return test_email_std()
    return test_email_form.test_email()

# region Email

def test_email_std():
    subject = 'Test email'
    sender = 'test@wags.org'
    message = ['test message £100']
    to = 'john.stembridge@gmail.com'
    cc=[]
    #use_sendmail(to=to, sender=sender, cc=cc, subject=subject, message=message)
    send_mail(to=to,
              sender=sender,
              cc=cc,
              subject='WAGS: ' + subject,
              message=message)
    form = SendEmailConfirmationForm()
    form.populate(subject, message)
    return render_template('user/event_booking_confirmation.html', form=form)


def test_email_to_andy():
    subject = 'Test email'
    sender = 'test@wags.org'
    message = ['Hi Andy']
    message.append('I noticed from logs on the wagsite that booking confirmation emails are being rejected by your email server.')
    message.append('I think the problem was at my end so have made a change and this is a test to see if the change worked.')
    message.append('If you receive this email, please let me know at john.stembridge@gmail.com')
    message.append('Thanks, John')
    to = 'andy@consult-lake.co.uk'
    cc=['john.stembridge@gmail.com']
    send_mail(to=to,
              sender=sender,
              cc=cc,
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
# endregion

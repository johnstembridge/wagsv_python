from flask import render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from globals.email import send_mail

def test_email():
    form = TestEmailForm()
    if form.is_submitted():
        if form.send.data:
            return form.send_email()
    else:
        form.populate()
        return render_template('admin/test_email.html', form=form)


class TestEmailForm(FlaskForm):
    recipient = StringField(label='Email address')
    from_address = StringField(label='From address')
    subject = StringField(label='Subject')
    message = TextAreaField(label='Message')
    send = SubmitField(label='Send')

    def populate(self):
        self.from_address.data = 'testing@wags.org'

    def send_email(self):
        to = self.recipient.data
        sender = self.from_address.data
        subject = self.subject.data
        message = self.message.data

        send_mail(to, sender, subject=subject, message=message)

        flash('email sent', 'success')
        form = SendEmailConfirmationForm()
        form.populate(subject, message.splitlines())
        return render_template('user/event_booking_confirmation.html', form=form)


class SendEmailConfirmationForm(FlaskForm):
    title = StringField(label='Title')
    message = StringField(label='Message')

    def populate(self, title, message):
        self.title.data = title
        self.message.data = message

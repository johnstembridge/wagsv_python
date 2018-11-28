from flask import current_app
from flask_sendmail import Message, Mail

from globals import config
from globals.decorators import async
from back_end.data_utilities import force_list
# from globals.app_setup import mail


@async
def send_async_email(app, msg):
    mail = Mail(app)
    with app.app_context():
        mail.send(msg)


def send_mail(to, sender, cc=None, subject=None, message=None):
    msg = Message(subject)
    msg.sender = sender
    msg.recipients = force_list(to)
    msg.cc = force_list(cc)
    msg.body = '\n'.join(message) if type(message) is list else message
    app = current_app._get_current_object()
    mail = Mail(app)
    if config.get('send_mail'):
        #send_async_email(app, msg)
        mail.send(msg)
    else:
        out = [
            'Email:',
            'from: ' + sender,
            'to: ' + ', '.join(to),
            'subject: ' + subject,
            'message:']
        print('\n'.join(out + message))

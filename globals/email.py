from flask import current_app
from flask_sendmail import Message

from globals.decorators import async
from back_end.data_utilities import force_list
from globals.app_setup import mail


@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_mail(to, sender, cc=None, subject=None, message=None):
    msg = Message(subject)
    msg.sender = sender
    msg.recipients = force_list(to)
    msg.cc = force_list(cc)
    msg.body = message
    app = current_app._get_current_object()
    send_async_email(app, msg)
    #mail.send(msg)


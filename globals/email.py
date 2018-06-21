from flask_sendmail import Message

from back_end.data_utilities import force_list
from globals.app_setup import mail


def send_mail(to, sender, cc, subject, message):
    msg = Message(subject)
    msg.sender = sender
    msg.recipients = force_list(to)
    msg.cc = force_list(cc)
    msg.body = message
    mail.send(msg)


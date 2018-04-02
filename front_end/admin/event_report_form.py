from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FieldList, FormField, HiddenField, SelectField

from globals.enumerations import PlayerStatus
from interface import get_event, get_event_scores


class EventReportForm(FlaskForm):
    event_name = StringField(label='Event name')
    winner = StringField(label='Winner')
    ntp = SelectField(label='Nearest the Pin')
    ld = SelectField(label='Longest Drive')
    event_type = HiddenField(label='Event type')
    event_id = HiddenField(label='Event_id')
    save = SubmitField(label='Save')

    def populate_event_report(self, year, event_id):
        event = get_event(year, event_id)
        self.event_name.data = '{} {} {}'.format(event['event'], event['venue'], event['date'])
        def lu_fn(vals):
            return vals['status'] == str(PlayerStatus.member.value)
        scores = get_event_scores(year, event_id).where(lu_fn)
        winner = ''


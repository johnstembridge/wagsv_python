from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, SelectField, TextAreaField

from front_end.form_helpers import set_select_field
from globals.enumerations import PlayerStatus
from back_end.interface import get_event, get_event_scores, get_player_name, get_player_names


class EventReportForm(FlaskForm):
    event_name = StringField(label='Event name')
    winner = StringField(label='Winner')
    ntp = SelectField(label='Nearest the Pin')
    ld = SelectField(label='Longest Drive')
    report = TextAreaField(label='Report')
    winner_return = HiddenField()
    save = SubmitField(label='Save')

    def populate_event_report(self, year, event_id):
        event = get_event(year, event_id)
        self.event_name.data = '{} {} {}'.format(event['event'], event['venue'], event['date'])

        def lu_fn(values):
            return values['status'] == str(PlayerStatus.member.value)
        all = get_event_scores(year, event_id)
        players = get_player_names(all.get_column('player'))
        members = all.where(lu_fn)
        pos = [int(s) for s in members.get_column('position')]
        pos = pos.index(min(pos))
        self.winner.data = get_player_name(members.get_column('player')[pos])
        self.winner_return.data = self.winner.data
        set_select_field(self.ntp, 'player', players)
        set_select_field(self.ld, 'player', players)

    def save_event_report(self, year, event_id):
        return True


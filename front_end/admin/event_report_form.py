from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, SelectField, TextAreaField

from back_end.file_access import get_file_contents
from front_end.form_helpers import set_select_field, get_elements_from_html
from globals.enumerations import PlayerStatus
from back_end.interface import get_event, get_event_scores


class EventReportForm(FlaskForm):
    event_name = StringField(label='Event name')
    winner = StringField(label='Winner')
    ntp = SelectField(label='Nearest the Pin')
    ld = SelectField(label='Longest Drive')
    report = TextAreaField(label='Report')
    winner_return = HiddenField()
    save = SubmitField(label='Save')

    def populate_event_report(self, event_id, report_file):
        event = get_event(event_id)
        self.event_name.data = event.full_name()

        all = get_event_scores(event_id)
        all.sort(['last_name', 'first_name'])
        if len(all.data) == 0:
            return False

        def lu_fn(values):
            return values['status'] == PlayerStatus.member
        members = all.where(lu_fn)
        players = all.get_columns('player_name')
        pos = [s for s in members.get_columns('position')]
        pos = pos.index(min(pos))
        self.winner.data = members.get_columns('player_name')[pos]
        self.winner_return.data = self.winner.data
        set_select_field(self.ntp, 'player', players)
        set_select_field(self.ld, 'player', players)
        report = get_file_contents(report_file)
        if report:
            values = get_elements_from_html(report, ['ld', 'ntp', 'report'])
            if len(values) == 0:
                values = self.alt_get_report_elements_from_html(report, {'ld': 'Longest Drive:', 'ntp': 'Nearest the Pin:'})
            self.ntp.data = values['ntp']
            self.ld.data = values['ld']
            self.report.data = values.get('report') or ''
        return True

    @staticmethod
    def alt_get_report_elements_from_html(html, items, ):
        # for old report files
        result = {}
        for item in items:
            text = items[item] + '</td><td>'
            start = len(text) + html.find(text)
            length = html[start:].find('<')
            result[item] = html[start: start + length]
        return result

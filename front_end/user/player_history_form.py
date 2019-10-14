from flask_wtf import FlaskForm
from wtforms import StringField, FormField, FieldList, HiddenField
from wtforms.fields.html5 import DateField
from back_end.interface import get_player, get_all_scores, get_scores_for_player
from back_end.data_utilities import fmt_date


class PlayerEventForm(FlaskForm):
    date = DateField(label='Date')
    course = StringField(label='Course')
    position = StringField(label='Position')
    points = StringField(label='Points')
    strokes = StringField(label='Shots')
    handicap = StringField(label='Handicap')
    status = StringField(label='Status')


class PlayerHistoryForm(FlaskForm):
    player = StringField(label='Player')
    year = StringField(label='Year')
    history = FieldList(FormField(PlayerEventForm))

    def populate_history(self, player_id, year=None):
        player = get_player(player_id)
        self.player.data = player.full_name()
        self.year.data = year or ''
        events = self.get_player_history(player_id, year)
        for item in events.data:
            item_form = PlayerEventForm()
            item_form.date = fmt_date(item[events.column_index('date')])
            item_form.course = item[events.column_index('course')]
            item_form.position = item[events.column_index('position')]
            item_form.points = item[events.column_index('points')]
            item_form.strokes = item[events.column_index('shots')]
            item_form.handicap = item[events.column_index('handicap')]
            item_form.status = player.state_as_of(item[events.column_index('date')]).status.name # item[events.column_index('status')].name
            self.history.append_entry(item_form)

    @staticmethod
    def get_player_history(player_id, year=None):
        hist = get_scores_for_player(player_id=player_id, year=year)
        hist.sort('date', reverse=year is None)
        return hist


class PlayerSummaryForm(FlaskForm):
    player = StringField(label='Player')
    count = StringField(label='Count')
    status = StringField(label='Status')
    first_game = DateField(label='First Game')
    player_id = HiddenField(label='Player Id')


class SummaryHistoryForm(FlaskForm):
    history = FieldList(FormField(PlayerSummaryForm))

    def populate_summary_history(self):
        hist = get_all_scores()
        for item in hist.data:
            item_form = PlayerSummaryForm()
            item_form.player_id = item[hist.column_index('player_id')]
            item_form.player = item[hist.column_index('player')]
            item_form.status = item[hist.column_index('status')]
            item_form.count = item[hist.column_index('count')]
            item_form.first_game = item[hist.column_index('first_game')]
            self.history.append_entry(item_form)

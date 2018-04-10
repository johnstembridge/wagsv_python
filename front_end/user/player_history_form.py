from flask_wtf import FlaskForm
from wtforms import StringField, FormField, FieldList
from wtforms.fields.html5 import DateField
from back_end.interface import get_player_name, get_player_id, get_player_scores, get_course_names, get_all_scores, \
    get_player_names
from back_end.data_utilities import is_num, normalise_name
from back_end.table import Table
from globals.enumerations import PlayerStatus


class PlayerEventForm(FlaskForm):
    date = DateField(label='Date')
    course = StringField(label='Course')
    position = StringField(label='Position')
    points = StringField(label='Points')
    strokes = StringField(label='Strokes')
    handicap = StringField(label='Handicap')
    status = StringField(label='Status')


class PlayerHistoryForm(FlaskForm):
    player = StringField(label='Player')
    year = StringField(label='Year')
    history = FieldList(FormField(PlayerEventForm))

    def populate_history(self, player_id, year=None):
        if not is_num(player_id):
            player_id = get_player_id(normalise_name(player_id))
        self.player.data = get_player_name(player_id)
        self.year.data = year or ''
        events = self.get_player_history(player_id, year)
        for item in events.data:
            item_form = PlayerEventForm()
            item_form.date = item[0]
            item_form.course = item[events.column_index('course_name')]
            item_form.position = item[events.column_index('position')]
            item_form.points = item[events.column_index('points')]
            item_form.strokes = item[events.column_index('strokes')]
            item_form.handicap = item[events.column_index('handicap')]
            item_form.status = 'member' if item[events.column_index('status')] == '1' else 'guest'
            self.history.append_entry(item_form)

    @staticmethod
    def get_player_history(player_id, year=None):
        hist = Table(*get_player_scores(player_id, year))
        hist.add_column('course_name', get_course_names(hist.get_columns('course')))
        hist.sort('date', reverse=year is None)
        return hist


class PlayerSummaryForm(FlaskForm):
    player = StringField(label='Player')
    count = StringField(label='Count')
    status = StringField(label='Status')
    first_game = DateField(label='First Game')
    # year_joined = StringField(label='Joined')


class SummaryHistoryForm(FlaskForm):
    history = FieldList(FormField(PlayerSummaryForm))

    def populate_summary_history(self):
        hist = self.get_summary_history()
        for item in hist.data:
            item_form = PlayerSummaryForm()
            item_form.player = item[hist.column_index('player')]
            item_form.status = item[hist.column_index('status')]
            item_form.count = item[hist.column_index('count')]
            item_form.first_game = item[hist.column_index('first_game')]
            self.history.append_entry(item_form)

    @staticmethod
    def get_summary_history():
        all_scores = Table(*get_all_scores([PlayerStatus.member.value, PlayerStatus.ex_member.value]))
        all_scores.add_column('player_name', get_player_names(all_scores.get_columns('player')))
        all_scores.sort(['player', 'date'])
        hist = []
        head = all_scores.head
        for player_id, scores in all_scores.groupby('player'):
            scores = list(scores)
            hist.append([
                scores[0][head.index('player_name')],
                PlayerStatus(int(scores[-1][head.index('status')])).name,
                len(scores),
                scores[0][head.index('date')]
            ])
        hist = Table(['player', 'status', 'count', 'first_game'], hist)
        hist.sort('count', reverse=True)
        return hist

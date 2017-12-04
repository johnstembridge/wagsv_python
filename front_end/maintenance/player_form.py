import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, TextAreaField, IntegerField, SubmitField, FieldList, \
    FormField, HiddenField
from wtforms_components import TimeField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField
#from interface import get_all_venue_names, get_all_event_names

class PlayerCardItemForm(FlaskForm):
    player_id = HiddenField(label='Player_id')
    player = StringField(label='Player')
    handicap = IntegerField(label='Handicap')
    guest = StringField(label='Guest')
    hole = IntegerField(label='Hole')
    par = IntegerField(label='Position')
    index = IntegerField(label='Index')
    strokes = IntegerField(label='Strokes')
    points = IntegerField(label='Points')

class PlayerCardForm(FlaskForm):
    scores = FieldList(FormField(PlayerCardItemForm))
    event_name = StringField(label='event_name')
    save_card = SubmitField(label='Save')
    editable = HiddenField(label='Editable')

    def populate_player_card(self, year, event_id, player_id):
        # event = get_event(year, event_id)
        # self.event_name.data = '{} {} {}'.format(event['event'], event['venue'], event['date'])
        # self.editable.data = 'y'  # if event['date'] <= datetime.date.today() else 'n'
        # players = get_results(year, event_id)
        num = 0
        # for player in players:
        #     num += 1
        #     item_form = EventResultItemForm()
        #     item_form.num = str(num)
        #     item_form.player = player['name']
        #     item_form.handicap = player['handicap']
        #     item_form.points = player['points']
        #     item_form.position = player['position']
        #     item_form.guest = player['guest']
        #     item_form.player_id = str(player['id'])
        #     self.scores.append_entry(item_form)

    def save_event_results(self, year, event_id):
        errors = self.errors
        if len(errors) > 0:
            return False
        fields = []
        data = []
        #   save_event_scores(year, event_id, fields, data)
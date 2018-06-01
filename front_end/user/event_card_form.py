from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FieldList, FormField, HiddenField

from back_end.interface import get_event, get_event_card, get_player


class EventCardItemForm(FlaskForm):
    hole = IntegerField(label='Hole')
    par = IntegerField(label='Par')
    si = IntegerField(label='SI')
    shots = IntegerField(label='Shots')
    points = IntegerField(label='Points')


class EventCardForm(FlaskForm):
    scoresOut = FieldList(FormField(EventCardItemForm))
    scoresIn = FieldList(FormField(EventCardItemForm))
    event_name = StringField(label='event_name')
    player = StringField(label='Player')
    handicap = StringField(label='Handicap')
    editable = HiddenField(label=None, id='editable')
    totalShotsOut = StringField(label='TotalShotsOut')
    totalPointsOut = StringField(label='TotalPointsOut')
    totalShotsIn = StringField(label='TotalShotsIn')
    totalPointsIn = StringField(label='TotalPointsIn')
    totalShots = StringField(label='TotalShots')
    totalPoints = StringField(label='TotalPoints')

    def populate_card(self, event_id, player_id):
        event = get_event(event_id)
        player = get_player(player_id)
        card = get_event_card(event_id, player_id)
        course_data = event.course.course_data_as_of(event.date.year)
        state = player.state_as_of(event.date)
        self.event_name.data = event.full_name()
        self.player.data = player.full_name()
        self.handicap.data = state.handicap

        holes = range(1, 19)
        for hole in holes:
            i = hole - 1
            shots = "-" if card[i] == 99 or card[i] is None else card[i]
            item_form = EventCardItemForm()
            item_form.hole = hole
            item_form.par = course_data.par[i]
            item_form.si = course_data.si[i]
            item_form.shots = shots
            item_form.points = 0
            if hole <= 9:
                self.scoresOut.append_entry(item_form)
            else:
                self.scoresIn.append_entry(item_form)

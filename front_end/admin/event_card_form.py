from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FieldList, FormField, HiddenField

from back_end.interface import get_event, save_event_score, get_event_card, get_player, get_event_scores, \
    save_event_result, calc_event_positions


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
    totalShotsReturn = HiddenField(label=None, id='totalShotsReturn')
    totalPointsReturn = HiddenField(label=None, id='totalPointsReturn')
    positionReturn = HiddenField(label=None, id='positionReturn')
    handicapReturn = HiddenField(label=None, id='handicapReturn')
    statusReturn = HiddenField(label=None, id='statusReturn')
    save_card = SubmitField(label='Save')

    def populate_card(self, event_id, player_id, position, handicap, status):
        event = get_event(event_id)
        course_data = event.course.course_data_as_of(event.date.year)
        card = get_event_card(event_id, player_id)

        self.event_name.data = event.full_name()
        self.player.data = get_player(player_id).full_name()
        self.handicap.data = handicap
        self.positionReturn.data = position
        self.handicapReturn.data = handicap
        self.statusReturn.data = status
        self.editable.data = event.is_result_editable()

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

    def save_event_card(self, event_id, player_id, form):
        errors = self.errors
        if len(errors) > 0:
            return False

        card = [d['shots'] for d in form.scoresOut.data] + [d['shots'] for d in form.scoresIn.data]
        card = [99 if v is None else v for v in card]
        total_shots = form.totalShotsReturn.data
        total_points = form.totalPointsReturn.data
        save_event_score(event_id, int(player_id), 0, card, total_shots, total_points)

        all_scores = get_event_scores(event_id)
        result = calc_event_positions(event_id, all_scores)
        save_event_result(event_id, result)

        return True

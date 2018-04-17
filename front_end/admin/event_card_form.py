from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FieldList, FormField, HiddenField

from back_end.calc import calc_event_positions
from back_end.interface import get_event, lookup_course, get_course_data, save_event_card, get_event_card, \
    get_player_name, is_event_result_editable, get_event_scores, save_event_scores, update_trophy_history
from globals.enumerations import PlayerStatus


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

    def populate_card(self, year, event_id, player_id, position, handicap, status):
        event = get_event(year, event_id)
        course_id = lookup_course(event['venue'])
        course_data = get_course_data(course_id, year)
        card = get_event_card(year, event_id, player_id)

        self.event_name.data = '{} {} {}'.format(event['event'], event['venue'], event['date'])
        self.player.data = get_player_name(player_id)
        self.handicap.data = handicap
        self.positionReturn.data = position
        self.handicapReturn.data = handicap
        self.statusReturn.data = status
        self.editable.data = is_event_result_editable(year, event_id)

        holes = range(1, 19)
        for hole in holes:
            i = str(hole)
            shots = "-" if card[i] == "99" or card[i] is None else card[i]
            item_form = EventCardItemForm()
            item_form.hole = hole
            item_form.par = int(course_data['par' + i])
            item_form.si = int(course_data['si' + i])
            item_form.shots = shots
            item_form.points = 0
            if hole <= 9:
                self.scoresOut.append_entry(item_form)
            else:
                self.scoresIn.append_entry(item_form)

    def save_event_card(self, year, event_id, player_id, form):
        errors = self.errors
        if len(errors) > 0:
            return False

        shots = [d['shots'] for d in form.scoresOut.data] + [d['shots'] for d in form.scoresIn.data]
        shots = ['99' if v is None else str(v) for v in shots]
        fields = [str(i) for i in range(1, 19)]
        save_event_card(year, event_id, player_id, fields, shots)

        handicap = form.handicapReturn.data
        status = str(PlayerStatus.member.value if form.statusReturn.data == '' else PlayerStatus.guest.value)
        total_shots = form.totalShotsReturn.data
        total_points = form.totalPointsReturn.data

        all_scores = get_event_scores(year, event_id).select_columns(
            ['player', 'position', 'points', 'strokes', 'handicap', 'status'])
        new = (player_id, '0', total_points, total_shots, handicap, status)
        all_scores.update_row('player', player_id, new)
        result = calc_event_positions(year, event_id, all_scores)
        save_event_scores(year, event_id, result)
        update_trophy_history(year, event_id, result)

        return True

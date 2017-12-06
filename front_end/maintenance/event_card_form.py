import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FieldList, FormField, HiddenField
from interface import get_event, lookup_course, get_course_data, save_event_card, get_player_handicap, \
    get_event_card, get_player_name, update_event_scores, is_latest_event
from data_utilities import fmt_date


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
    editable = HiddenField(label='Editable')
    totalShotsOut = StringField(label='TotalShotsOut')
    totalPointsOut = StringField(label='TotalPointsOut')
    totalShotsIn = StringField(label='TotalShotsIn')
    totalPointsIn = StringField(label='TotalPointsIn')
    totalShots = StringField(label='TotalShots')
    totalPoints = StringField(label='TotalPoints')
    totalShotsReturn = HiddenField(label=None, id='totalShotsReturn')
    totalPointsReturn = HiddenField(label=None, id='totalPointsReturn')
    save_card = SubmitField(label='Save')

    def populate_card(self, year, event_id, player_id):
        event = get_event(year, event_id)
        date = fmt_date(event['date'])
        course_id = lookup_course(event['venue']) + 1
        course_data = get_course_data(course_id, year)
        hcap = get_player_handicap(player_id, date)
        card = get_event_card(year, event_id, player_id)

        self.event_name.data = '{} {} {}'.format(event['event'], event['venue'], event['date'])
        self.player.data = get_player_name(player_id)
        self.handicap.data = hcap
        editable = datetime.date.today() > event['date'] and is_latest_event(int(event_id))
        self.editable.data = 'y' if editable else 'n'

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

        total_shots = form.totalShotsReturn.data
        total_points = form.totalPointsReturn.data
        update_event_scores(year, event_id, player_id, ["points", "strokes"], [total_points, total_shots])

        shots = [d['shots'] for d in form.scoresOut.data] + [d['shots'] for d in form.scoresIn.data]
        shots = ['99' if v is None else str(v) for v in shots]
        fields = [str(i) for i in range(1, 19)]
        save_event_card(year, event_id, player_id, fields, shots)

        return True

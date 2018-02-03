from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FieldList, FormField, HiddenField
from back_end.interface import get_event, lookup_course, get_course_data, get_player_handicap, \
    get_event_card, get_player_name, is_event_result_editable


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
    save_card = SubmitField(label='Save')

    def populate_card(self, year, event_id, player_id):
        event = get_event(year, event_id)
        course_id = lookup_course(event['venue'])
        course_data = get_course_data(course_id, year)
        hcap = get_player_handicap(player_id, event['date'])
        card = get_event_card(year, event_id, player_id)

        self.event_name.data = '{} {} {}'.format(event['event'], event['venue'], event['date'])
        self.player.data = get_player_name(player_id)
        self.handicap.data = hcap
        self.editable.data = False

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

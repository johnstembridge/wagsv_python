import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FieldList, FormField, HiddenField
from interface import get_course, get_course_data, save_event_card, update_event_scores


class CourseCardItemForm(FlaskForm):
    hole = StringField(label='Hole')
    par = IntegerField(label='Par')
    si = IntegerField(label='SI')


class CourseCardForm(FlaskForm):
    holesOut = FieldList(FormField(CourseCardItemForm))
    holesIn = FieldList(FormField(CourseCardItemForm))
    course_name = StringField(label='Course Name')
    editable = HiddenField(label='Editable')
    totalShotsOut = StringField(label='TotalShotsOut')
    totalShotsIn = StringField(label='TotalShotsIn')
    totalShots = StringField(label='TotalShots')
    save_card = SubmitField(label='Save')

    def populate_card(self, course_id):
        year = 2100
        course_data = get_course(course_id)
        course_card = get_course_data(course_id, year)

        self.course_name = 'new' if course_id == 0 else course_data['name']
        self.editable = True  # datetime.date.today() > event['date'] and is_latest_event(event_id)
        shots_out = 0
        shots_in = 0
        holes = range(1, 19)
        for hole in holes:
            i = str(hole)
            item_form = CourseCardItemForm()
            item_form.hole = hole
            item_form.par = int(course_card['par' + i])
            item_form.si = int(course_card['si' + i])
            if hole <= 9:
                shots_out += int(course_card['par' + i])
                self.holesOut.append_entry(item_form)
            else:
                shots_in += int(course_card['par' + i])
                self.holesIn.append_entry(item_form)
        self.totalShotsOut = shots_out
        self.totalShotsIn = shots_in

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

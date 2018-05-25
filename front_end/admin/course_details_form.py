from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FieldList, FormField, HiddenField
from wtforms.validators import ValidationError
from back_end.interface import get_course, save_course


class CourseCardItemForm(FlaskForm):
    hole = StringField(label='Hole')
    par = IntegerField(label='Par')
    si = IntegerField(label='SI')


class CourseCardForm(FlaskForm):
    course_name = StringField(label='Course Name')
    sss = IntegerField(label='SSS')
    holesOut = FieldList(FormField(CourseCardItemForm))
    holesIn = FieldList(FormField(CourseCardItemForm))
    new_course = HiddenField(label='New Course')
    editable = HiddenField(label='Editable')
    totalParOut = StringField(label='TotalParOut')
    totalParIn = StringField(label='TotalParIn')
    totalPar = StringField(label='TotalPar')
    save_card = SubmitField(label='Save')
    whole_form = HiddenField(label='Whole Form Validation')
    year = HiddenField(label="CourseData year")

    def populate_card(self, course_id):
        new = course_id == 0
        self.new_course.data = new
        year = 3000  # get latest
        self.year.data = year
        course = get_course(course_id)
        self.course_name.data = '' if new else course.name
        course_card = course.course_data_as_of(year)
        new = not course_card
        self.sss.data = 0 if new else course_card.sss
        self.editable.data = True  # datetime.date.today() > event.date and is_latest_event(event_id)
        par_out = 0
        par_in = 0
        holes = range(1, 19)
        for hole in holes:
            i = hole - 1
            item_form = CourseCardItemForm()
            item_form.hole = str(hole)
            if new:
                pass
                item_form.par = 0
                item_form.si = 0
            else:
                item_form.par = course_card.par[i]
                item_form.si = course_card.si[i]
            if hole <= 9:
                par_out += item_form.par
                self.holesOut.append_entry(item_form)
            else:
                par_in += item_form.par
                self.holesIn.append_entry(item_form)
        self.totalParOut = par_out
        self.totalParIn = par_in
        self.totalPar = par_out + par_in

    def validate_whole_form(self, fields):
        errors = []
        count = [0]*18
        for si in [d['si'] for d in self.holesOut.data] + [d['si'] for d in self.holesIn.data]:
            if si in range(1, 19):
                count[si-1] += 1
            else:
                errors.append('Stroke index {} out of range'.format(si))
        for hole in range(1, 19):
            if count[hole - 1] == 0:
                errors.append('Stroke index {} missing'.format(hole))
            if count[hole-1] > 1:
                errors.append('Duplicate stroke index {}'.format(hole))
        if errors:
            raise ValidationError('; '.join(errors))

    def save_course_card(self, venue_id, course_id):
        errors = self.errors
        if len(errors) > 0:
            return False
        year = int(self.year.data)
        sss = self.sss.data
        si = [d['si'] for d in self.holesOut.data] + [d['si'] for d in self.holesIn.data]
        par = [d['par'] for d in self.holesOut.data] + [d['par'] for d in self.holesIn.data]
        course = {
            'name': self.course_name.data,
            'venue_id': venue_id,
            'sss': sss,
            'si': si,
            'par': par,
            'year': year
        }
        save_course(course_id, course)

        return True

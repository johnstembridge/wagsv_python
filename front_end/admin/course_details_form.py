import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FieldList, FormField, HiddenField
from wtforms.validators import ValidationError
from back_end.interface import get_course, save_course, get_course_data


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
    add_new_card = SubmitField(label='Add New Card')
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

    def save_course_card(self, venue_id, course_id, add_new_card):
        errors = self.errors
        if len(errors) > 0:
            return False
        year = int(self.year.data)
        course = get_course(course_id)
        if course_id == 0:
            # new course
            course.name = self.course_name.data
            course.venue_id = venue_id
            course_data = get_course_data(0, 0)
            course_data.year = year
            course.cards.append(course_data)
        else:
            course_data = get_course_data(course_id, year)

        sss = self.sss.data
        si = [d['si'] for d in self.holesOut.data] + [d['si'] for d in self.holesIn.data]
        par = [d['par'] for d in self.holesOut.data] + [d['par'] for d in self.holesIn.data]
        if add_new_card and year == 3000:
            # rename previous card
            course_data.year = datetime.date.today().year - 1
            # create new
            new_course_data = get_course_data(0, 0)
            new_course_data.course_id = course_id
            new_course_data.year = year
            new_course_data.sss = sss
            new_course_data.si = si
            new_course_data.par = par
            course.cards.append(new_course_data)
        else:
            course_data.sss = sss
            course_data.si = si
            course_data.par = par

        save_course(course)

        return True

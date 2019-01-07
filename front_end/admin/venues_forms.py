from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, TextAreaField, SelectField, FieldList, FormField
from back_end.interface import get_venue_select_choices, get_venue, save_venue, get_course_select_choices, get_course
from front_end.form_helpers import set_select_field, set_select_field_new
from models.wags_db import Contact


class VenueListForm(FlaskForm):
    venue = SelectField(label='Venue')
    edit_venue = SubmitField(label='Edit Venue')
    add_venue = SubmitField(label='Add Venue')
    editable = HiddenField(label='Editable')

    def populate_venue_list(self):
        set_select_field(self.venue, 'venue', get_venue_select_choices(), '')
        self.editable = True


class VenueCourseForm(FlaskForm):
    id = HiddenField(label='Id')
    name = StringField(label='Name')


class VenueDetailsForm(FlaskForm):
    name = StringField(label='Name')
    venue_id = HiddenField(label='Venue Id')
    url = StringField(label='url')
    phone = StringField(label='Phone')
    post_code = StringField(label='Post Code')
    address = TextAreaField(label='Address', default='')
    directions = TextAreaField(label='Directions', default='')
    editable = HiddenField(label='Editable')
    courses = FieldList(FormField(VenueCourseForm))
    select_course = SelectField(coerce=int)
    add_course = SubmitField(label='Add')
    remove_course = SubmitField(label='Remove')
    new_course = SubmitField(label='New Course')
    save = SubmitField(label='Save')

    def populate_venue(self, venue_id):
        self.editable.data = True
        venue = get_venue(venue_id)
        self.venue_id = venue.id
        self.name.data = venue.name
        self.directions.data = venue.directions
        course_choices = get_course_select_choices()
        set_select_field_new(self.select_course, course_choices, item_name='Course')
        if venue.contact:
            self.url.data = venue.contact.url
            self.phone.data = venue.contact.phone
            self.post_code.data = venue.contact.post_code
            self.address.data = venue.contact.address
        for course in venue.courses:
            item_form = VenueCourseForm()
            item_form.id = course.id
            item_form.name = course.name
            self.courses.append_entry(item_form)

    def save_venue(self, venue_id):
        errors = self.errors
        if len(errors) > 0:
            return False
        venue = get_venue(venue_id)
        venue.name = self.name.data
        if not venue.contact:
            venue.contact = Contact()
        venue.contact.url = self.url.data
        venue.contact.phone = self.phone.data
        venue.contact.post_code = self.post_code.data
        venue.contact.address = self.address.data
        venue.directions = self.directions.data
        selected_course_id = self.select_course.data
        if self.add_course.data and selected_course_id > 0:
            if selected_course_id not in [c.id for c in venue.courses]:
                venue.courses.append(get_course(selected_course_id))
        if self.remove_course.data and selected_course_id > 0:
            if selected_course_id in [c.id for c in venue.courses]:
                venue.courses.remove(get_course(selected_course_id))
        venue_id = save_venue(venue)
        return True

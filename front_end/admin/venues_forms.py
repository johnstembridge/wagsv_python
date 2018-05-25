from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, TextAreaField, SelectField, FieldList, FormField
from back_end.interface import get_venue_select_list, get_venue, save_venue
from front_end.form_helpers import set_select_field


class VenueListForm(FlaskForm):
    venue = SelectField(label='Venue')
    edit_venue = SubmitField(label='Edit Venue')
    add_venue = SubmitField(label='Add Venue')
    editable = HiddenField(label='Editable')

    def populate_venue_list(self):
        set_select_field(self.venue, 'venue', get_venue_select_list(), '')
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
    add_course = SubmitField(label='Add Course')
    save = SubmitField(label='Save')

    def populate_venue(self, venue_id):
        self.editable.data = True
        venue = get_venue(venue_id)
        self.venue_id = venue.id
        self.name.data = venue.name
        self.directions.data = venue.directions
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
        venue = {
            'name': self.name.data,
            'url': self.url.data,
            'phone': self.phone.data,
            'post_code': self.post_code.data,
            'address': self.address.data,
            'directions': self.directions.data
        }
        venue_id = save_venue(venue_id, venue)
        return True

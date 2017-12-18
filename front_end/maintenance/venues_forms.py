from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, TextAreaField, SelectField, FieldList, FormField
from interface import get_venue_select_list, get_venue, save_venue, get_new_venue_id, get_courses_for_venue
from form_helpers import set_select_field


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
    submit = SubmitField(label='Save')

    def populate_venue(self, venue_id):
        self.editable.data = True
        venue = get_venue(venue_id)
        self.venue_id = venue['id']
        self.name.data = venue['name']
        self.url.data = venue['url']
        self.phone.data = venue['phone']
        self.post_code.data = venue['post_code']
        self.address.data = venue['address']
        self.directions.data = venue['directions']
        keys, courses = get_courses_for_venue(venue['id'])
        for course in courses:
            c = dict(zip(keys, course))
            item_form = VenueCourseForm()
            item_form.id = c['id']
            item_form.name = c['name']
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
        if venue_id == "0":
            venue_id = str(get_new_venue_id())

        save_venue(venue_id, venue)
        return True

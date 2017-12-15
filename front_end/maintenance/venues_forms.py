from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, TextAreaField, SelectField
from interface import get_all_venue_names, get_venue, save_venue, get_new_venue_id
from data_utilities import decode_address, encode_address
from form_helpers import set_select_field


class VenueItemForm(FlaskForm):
    id = HiddenField(label='Id')
    name = StringField(label='Name')


class VenueListForm(FlaskForm):
    all_venues = get_all_venue_names()
    venue = SelectField(label='Venue')
    edit_venue = SubmitField(label='Edit Venue')
    add_venue = SubmitField(label='Add Venue')
    editable = HiddenField(label='Editable')

    def populate_venue_list(self):
        set_select_field(self.venue, 'venue', get_all_venue_names(), '')
        self.editable = True


class VenueDetailsForm(FlaskForm):
    name = StringField(label='Name')
    url = StringField(label='url')
    phone = StringField(label='Phone')
    post_code = StringField(label='Post Code')
    address = TextAreaField(label='Address', default='')
    directions = TextAreaField(label='Directions', default='')
    editable = HiddenField(label='Editable')
    submit = SubmitField(label='Save')

    def populate_venue(self, venue_id):
        self.editable.data = True
        venue = get_venue(venue_id)
        self.name.data = venue['name']
        self.url.data = venue['url']
        self.phone.data = venue['phone']
        self.post_code.data = venue['post_code']
        self.address.data = decode_address(venue['address'])
        self.directions.data = venue['directions']

    def save_venue(self, venue_id):
        errors = self.errors
        if len(errors) > 0:
            return False
        venue = {
            'name': self.name.data,
            'url': self.url.data,
            'phone': self.phone.data,
            'post_code': self.post_code.data,
            'address': encode_address(self.address.data),
            'directions': self.directions.data
        }
        if venue_id == "0":
            venue_id = str(get_new_venue_id())

        save_venue(venue_id, venue)
        return True

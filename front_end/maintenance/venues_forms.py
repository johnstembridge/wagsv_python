from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FieldList, FormField, HiddenField, TextAreaField
from interface import get_all_venues, get_venue, save_venue


class VenueItemForm(FlaskForm):
    id = HiddenField(label='Id')
    name = StringField(label='Name')


class VenueListForm(FlaskForm):
    venue_list = FieldList(FormField(VenueItemForm))
    add_venue = SubmitField(label='Add Venue')
    editable = HiddenField(label='Editable')

    def populate_venue_list(self):
        self.editable = True
        for item in get_all_venues():
            item_form = VenueItemForm()
            item_form.id = item['id']
            item_form.name = item['name']
            self.venue_list.append_entry(item_form)


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
        self.address.data = venue['address']
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
            'address': self.address.data,
            'directions': self.directions.data
        }
        if venue_id == "0":
            venue_id = str(get_new_venue_id())

        save_venue(venue_id, venue)
        return True

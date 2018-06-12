import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, FieldList, FormField, HiddenField, SelectField, SubmitField
from wtforms.fields.html5 import DateField
from back_end.data_utilities import encode_date_short
from front_end.form_helpers import set_select_field_new
from globals.config import url_for_user
from globals.enumerations import EventType
from back_end.interface import get_event_list, get_venue_url, get_event_select_list, is_event_bookable, \
    get_events_for_year


class EventItemForm(FlaskForm):
    num = HiddenField(label='id')
    date = DateField(label='Date')
    event = StringField(label='Event')
    trophy_url = StringField(label='Link to Trophy')
    venue_url = StringField(label='Link to Venue')
    venue = StringField(label='Venue')
    event_type = HiddenField(label='Event type')
    bookable = HiddenField(label='Event bookable')
    result = HiddenField(label='Result available')
    new_section = HiddenField(label='Start new section')


class EventListForm(FlaskForm):
    event_list = FieldList(FormField(EventItemForm))

    def populate_event_list(self, year):
        first = True
        for event in get_events_for_year(year):
            event_type = event.type
            item_form = EventItemForm()
            item_form.num = event.id
            item_form.date = encode_date_short(event.date)
            if event.trophy:
                item_form.event = event.trophy.name
                item_form.trophy_url = event.trophy.url()
            else:
                item_form.event = ''
                item_form.trophy_url = None
            item_form.venue = event.venue.name
            item_form.venue_url = get_venue_url(event.venue)

            item_form.event_type = event_type.name
            item_form.new_section = not (first or event.tour_event_id)
            first = False
            item_form.bookable = is_event_bookable(event)
            item_form.result = event.date < datetime.date.today() and event.type in (EventType.wags_vl_event, EventType.wags_tour)
            self.event_list.append_entry(item_form)


class EventSelectForm(FlaskForm):
    event = SelectField(label='Select Event', coerce=int)
    show_result = SubmitField(label='Show Result')

    def populate_event_select(self):
        set_select_field_new(self.event, get_event_select_list(), item_name='Event')

    def show_event_result(self):
        event_id = self.event.data
        return url_for_user('results_event', event_id=event_id)


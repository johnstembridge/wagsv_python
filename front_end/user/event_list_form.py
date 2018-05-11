import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, FieldList, FormField, HiddenField, SelectField, SubmitField
from wtforms.fields.html5 import DateField
from back_end.data_utilities import encode_date_short, in_date_range, parse_date
from front_end.form_helpers import set_select_field
from globals.config import url_for_user
from globals.enumerations import EventType
from models.wags_db import Event
from back_end.interface import get_event_list, get_trophy_url, is_tour_event, get_venue_url, get_event_select_list, \
    get_event_by_year_and_name


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
        tour_event = ''
        for item in get_event_list(year):
            event_type = item['type']
            item_form = EventItemForm()
            item_form.num = item['num']
            item_form.date = encode_date_short(item['date'])
            item_form.event = item['event']
            item_form.venue = item['venue']
            item_form.venue_url = get_venue_url(year, item['venue_url'])
            item_form.trophy_url = item['trophy_url']
            item_form.event_type = event_type.value
            item_form.new_section = not (first or item['tour_id'])
            first = False
            # bookable:  1 - booking open, 0 - booking closed, -1 - booking not applicable
            item_form.bookable = \
                1 if in_date_range(datetime.date.today(), item['start_booking'], item['end_booking']) \
                else -1 if (is_tour_event(item) or (True if not item['start_booking'] else datetime.date.today() < item['start_booking'])) \
                else 0
            item_form.result = item['date'] < datetime.date.today()
            self.event_list.append_entry(item_form)


class EventSelectForm(FlaskForm):
    event = SelectField(label='Select Event')
    show_result = SubmitField(label='Show Result')

    def populate_event_select(self):
        set_select_field(self.event, None, get_event_select_list(), '')

    def show_event_result(self):
        date, course = self.event.data.split('-')
        year = parse_date(date).year
        event_id = get_event_by_year_and_name(year, course)['num']
        if event_id:
            return url_for_user('results_event', year=year, event_id=event_id)
        else:
            return url_for_user('results_event_date', date=date.replace('/', '-'))

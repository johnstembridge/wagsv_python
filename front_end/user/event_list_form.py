import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, FieldList, FormField, HiddenField
from wtforms.fields.html5 import DateField
from back_end.interface import get_event_list, get_trophy_url, is_tour_event
from back_end.data_utilities import encode_date_short, in_date_range


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
            item_form = EventItemForm()
            item_form.num = item['num']
            item_form.date = encode_date_short(item['date'])
            item_form.event = item['event']
            item_form.venue = item['venue']
            item_form.venue_url = item['venue_url']
            item_form.trophy_url = get_trophy_url(item['event'])
            item_form.event_type = item['type']
            if item['type'] == 'wags_tour':
                tour_event = item['event']
            item_form.new_section = not (first or is_tour_event(item))
            first = False
            if is_tour_event(item) and tour_event == item['event']:
                item_form.event = ''
            # bookable:  1 - booking open, 0 - booking closed, -1 - booking not applicable
            item_form.bookable = \
                1 if in_date_range(datetime.date.today(), item['start_booking'], item['end_booking']) \
                else -1 if (is_tour_event(item) or (True if not item['start_booking'] else datetime.date.today() < item['start_booking'])) \
                else 0
            item_form.result = item['date'] < datetime.date.today()
            self.event_list.append_entry(item_form)

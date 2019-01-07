import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FieldList, FormField, HiddenField

from back_end.data_utilities import fmt_date
from back_end.interface import is_event_editable, get_events_for_year
from globals import config
from globals.enumerations import EventType


class EventItemForm(FlaskForm):
    date = StringField(label='Date')
    event = StringField(label='Event')
    venue = StringField(label='Venue')
    event_id = HiddenField(label='id')
    event_type = HiddenField(label='Event type')
    result = HiddenField(label='Result available')


class EventListForm(FlaskForm):
    event_list = FieldList(FormField(EventItemForm))
    add_event = SubmitField(label='Add Event')
    add_tour = SubmitField(label='Add Tour')
    add_non = SubmitField(label='Add Non Event')
    editable = HiddenField(label='Editable')

    def populate_event_list(self, year):
        self.editable.data = is_event_editable(year)
        override = config.get('override')
        for event in get_events_for_year(year):
            event_type = event.type
            item_form = EventItemForm()
            item_form.event_id = event.id
            item_form.date = fmt_date(event.date)
            item_form.event = event.trophy.name if event.trophy else ''
            item_form.venue = event.course.name if event_type == EventType.wags_vl_event else event.venue.name or ''
            item_form.event_type = event_type.value
            item_form.result = override or event.date < datetime.date.today() and event.type in (EventType.wags_vl_event, EventType.wags_tour)
            self.event_list.append_entry(item_form)


import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FieldList, FormField, HiddenField

from back_end.data_utilities import fmt_date, add_http
from back_end.interface import get_events_for_year, is_event_list_editable

from globals import config
from globals.enumerations import EventType


class EventItemForm(FlaskForm):
    date = StringField(label='Date')
    event = StringField(label='Event')
    venue = StringField(label='Venue')
    event_id = HiddenField(label='id')
    event_type = HiddenField(label='Event type')
    event_bookable = HiddenField(label='Event bookable')
    event_viewable = HiddenField(label='Event viewable')
    result = HiddenField(label='Result available')


class EventListForm(FlaskForm):
    event_list = FieldList(FormField(EventItemForm))
    add_event = SubmitField(label='Add Event')
    add_tour = SubmitField(label='Add Tour')
    add_non_vl = SubmitField(label='Add Non-VL Event')
    add_non = SubmitField(label='Add Non Event')
    publish_calendar = SubmitField(label='Publish Calendar')
    editable = HiddenField(label='Editable')

    def populate_event_list(self, year):
        self.editable.data = is_event_list_editable(year)
        override = config.get('override')
        for event in get_events_for_year(year):
            item_form = EventItemForm()
            item_form.event_id = event.id
            item_form.date = fmt_date(event.date)
            item_form.event = event.trophy.name if event.trophy else ''
            item_form.venue = event.venue.name
            item_form.event_type = event.type
            item_form.event_bookable = event.is_bookable() or event.are_tour_bookings_editable()
            item_form.event_viewable = event.is_viewable() or event.tour_event_id
            item_form.result = override or \
                               (event.date <= datetime.date.today() and
                                event.type in
                                [EventType.wags_vl_event, EventType.non_vl_event])
            self.event_list.append_entry(item_form)


class EventCalendarItemForm:
    date = ''
    name = ''
    location = ''
    description = ''
    all_day = ''
    event_start_time = ''
    event_end_time = ''
    link = ''
    link_description = ''


class EventCalendarListForm():
    event_calendar_list = []

    def populate_calendar_event_list(self, year):
        for event in get_events_for_year(year):
            if event.type in [EventType.wags_vl_event, EventType.non_vl_event,
                              EventType.non_event] and event.venue.contact:
                item_form = EventCalendarItemForm()
                item_form.name = "WAGS - " + (event.trophy.name if event.trophy else event.venue.name)
                item_form.date = fmt_date(event.date, '%Y-%m-%d')
                item_form.location = event.venue.name
                item_form.all_day = 'N' if event.type in [EventType.wags_vl_event, EventType.non_vl_event] else 'Y'
                schedule = event.schedule
                if item_form.all_day == 'N' and len(schedule) > 0:
                    item_form.event_start_time = schedule[0].time.strftime('%H:%M')
                    item_form.event_end_time = schedule[-1].time.strftime('%H:%M')
                else:
                    item_form.all_day = 'Y'
                item_form.link = add_http(event.venue.contact.url)
                item_form.link_description = 'Go to venue'
                self.event_calendar_list.append(item_form)

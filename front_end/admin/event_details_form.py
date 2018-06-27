import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, TextAreaField, IntegerField, SubmitField, FieldList, \
    FormField, HiddenField
from wtforms.fields.html5 import DateField
from wtforms_components import TimeField

from front_end.form_helpers import set_select_field_new
from globals.enumerations import EventType
from back_end.interface import get_event, get_trophy_select_choices, save_event_details, \
    is_event_editable, get_member_select_choices, get_venue_select_choices, get_course_select_choices
from models.wags_db import Event, Schedule


class ScheduleForm(FlaskForm):
    time = TimeField('Time')
    text = StringField('Item')


class TourScheduleForm(FlaskForm):
    date = DateField('Date')
    course = StringField(label='Course')


class EventForm(FlaskForm):
    date = DateField(label='Date')
    trophy = SelectField(label='Trophy', coerce=int)
    venue = SelectField(label='Venue', coerce=int)
    course = SelectField(label='Course', coerce=int)
    organiser = SelectField(label='Organiser', coerce=int)
    member_price = DecimalField(label='Member Price')
    guest_price = DecimalField(label='Guest Price')
    start_booking = DateField(label='Booking Starts')
    end_booking = DateField(label='Booking Ends')
    max = IntegerField(label='Maximum')
    event_type = HiddenField(label='Event Type')
    schedule = FieldList(FormField(ScheduleForm))
    tour_schedule = FieldList(FormField(TourScheduleForm))
    note = TextAreaField(label='Notes', default='')
    submit = SubmitField(label='Save')
    editable = HiddenField(label='Editable')

    def populate_event(self, event_id, event_type):
        event = get_event(event_id)
        event_type = event_type or event.type
        self.editable = is_event_editable(event.date.year)
        self.date.data = event.date
        organiser = event.organiser.id if event.organiser else 0
        trophy = event.trophy.id if event.trophy else 0
        venue = event.venue.id if event.venue else 0
        course = event.course.id if event.course else 0
        course_choices = get_course_select_choices()

        self.member_price.data = event.member_price
        self.guest_price.data = event.guest_price
        self.start_booking.data = event.booking_start
        self.end_booking.data = event.booking_end
        self.max.data = event.max
        self.event_type.data = event_type.value
        self.note.data = event.note
        set_select_field_new(self.organiser, get_member_select_choices(), default_selection=organiser,
                             item_name='Organiser')
        set_select_field_new(self.trophy, get_trophy_select_choices(), default_selection=trophy, item_name='Trophy')
        set_select_field_new(self.venue, get_venue_select_choices(), default_selection=venue, item_name='Venue')
        if event_type in [EventType.wags_vl_event, EventType.non_event]:
            set_select_field_new(self.course, course_choices, default_selection=course, item_name='Course')
            for item in event.schedule + (6 - len(event.schedule)) * [Schedule()]:
                item_form = ScheduleForm()
                item_form.time = item.time
                item_form.text = item.text
                self.schedule.append_entry(item_form)
        if event_type == EventType.wags_tour:
            for item in event.tour_events + (6 - len(event.tour_events)) * [Event()]:
                item_form = TourScheduleForm()
                item_form.date = item.date
                course = item.course.name if item.course else ''
                item_form.course = course

                self.tour_schedule.append_entry(item_form)
                pass
        return event_id

    def save_event(self, event_id):
        errors = self.errors
        if len(errors) > 0:
            return False
        event_type = EventType(int(self.event_type.data))
        event = {
            'venue_id': self.venue.data,
            'date': self.date.data,
            'trophy_id': self.trophy.data,
            'course_id': self.course.data,
            'organiser_id': self.organiser.data,
            'member_price': self.member_price.data,
            'guest_price': self.guest_price.data,
            'start_booking': self.start_booking.data,
            'end_booking': self.end_booking.data,
            'max': self.max.data or '0',
            'event_type': event_type,
            'note': self.note.data,
            'schedule': [],
            'tour_schedule': []
        }

        if event_type == EventType.wags_vl_event:
            for item in self.schedule.data:
                event['schedule'].append(item)

        if event_type == EventType.wags_tour:
            event['course_id'] = None
            for item in self.tour_schedule.data:
                if item['date'] and item['course']:
                    event['tour_schedule'].append(item)

        event_id = save_event_details(event_id, event)

        return True

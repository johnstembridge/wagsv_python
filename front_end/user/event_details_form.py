import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, TextAreaField, IntegerField, SubmitField, FieldList, \
    FormField, HiddenField
from wtforms.fields.html5 import DateField
from wtforms_components import TimeField

from back_end.players import Players
from front_end.form_helpers import set_select_field
from globals.enumerations import EventType
from back_end.interface import get_all_venue_names, get_all_course_names, get_event, save_event, \
    get_new_event_id, get_tour_events, get_all_trophy_names, create_bookings_file


class ScheduleForm(FlaskForm):
    time = TimeField('Time')
    text = StringField('Item')


class TourScheduleForm(FlaskForm):
    date = DateField('Date')
    course = StringField(label='Course')


class EventForm(FlaskForm):
    date = DateField(label='Date')
    trophy = SelectField(label='Trophy')
    venue = SelectField(label='Venue')
    course = SelectField(label='Course')
    organiser = SelectField(label='Organiser')
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

    def populate_event(self, year, event_id, event_type):
        self.editable = year >= datetime.date.today().year
        event = get_event(year, event_id)
        self.date.data = event['date']
        set_select_field(self.organiser, 'organiser', Players().get_current_members(), event['organiser'])
        self.member_price.data = event['member_price']
        self.guest_price.data = event['guest_price']
        self.start_booking.data = event['start_booking']
        self.end_booking.data = event['end_booking']
        self.max.data = event['max']
        self.event_type.data = event_type.name
        self.note.data = event['note']
        set_select_field(self.trophy, 'trophy', get_all_trophy_names(), event['event'])
        set_select_field(self.venue, 'venue', get_all_venue_names(), event['venue'])
        if event_type in [EventType.wags_vl_event, EventType.non_event]:
            set_select_field(self.course, 'course', get_all_course_names(), event['course'])
            for item in event['schedule']:
                item_form = ScheduleForm()
                item_form.time = item['time']
                item_form.text = item['text']
                self.schedule.append_entry(item_form)
        if event_type == EventType.wags_tour:
            for item in get_tour_events(year, event_id, 6):
                item_form = TourScheduleForm()
                item_form.date = item['date']
                item_form.course = item['course']
                self.tour_schedule.append_entry(item_form)
        return event_id

    def save_event(self, year, event_id):
        errors = self.errors
        if len(errors) > 0:
            return False
        event = {
            'venue': self.venue.data,
            'date': self.date.data,
            'event': self.trophy.data,
            'course': self.course.data,
            'organiser': self.organiser.data,
            'member_price': self.member_price.data,
            'guest_price': self.guest_price.data,
            'start_booking': self.start_booking.data,
            'end_booking': self.end_booking.data,
            'max': self.max.data or '0',
            'event_type': self.event_type.data,
            'note': self.note.data,
            'schedule': [],
            'tour_schedule': []
        }
        if event_id == "0":
            event_id = str(get_new_event_id(year))

        if EventType[self.event_type.data] == EventType.wags_vl_event:
            for item in self.schedule.data:
                event['schedule'].append(item)
            if self.start_booking.data and self.start_booking.data <= datetime.date.today():
                create_bookings_file(year, event_id)

        if EventType[self.event_type.data] == EventType.wags_tour:
            event['course'] = ''
            tour_event_id = int(event_id)
            for item in self.tour_schedule.data:
                if item['date'] and item['course']:
                    tour_event_id += 0.1
                    id = '{0:.1f}'.format(tour_event_id)
                    item.update({
                        'num': id,
                        'date': item['date'],
                        'venue': item['course'],
                        'event': self.trophy.data,
                        'course': item['course'],
                        'event_type': EventType.wags_vl_event.name,
                        'start_booking': None,
                        'end_booking': None,
                        'member_price': None,
                        'guest_price': None,
                        'schedule': [],
                        'organiser': self.organiser.data
                    })
                    event['tour_schedule'].append(item)
                    save_event(year, id, item)

        save_event(year, event_id, event)

        return True

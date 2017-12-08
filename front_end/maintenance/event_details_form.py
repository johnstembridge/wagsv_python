import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, TextAreaField, IntegerField, SubmitField, FieldList, \
    FormField, HiddenField
from wtforms_components import TimeField
from wtforms.fields.html5 import DateField
from interface import get_all_venue_names, get_all_event_types, get_all_event_names, get_event, save_event, \
    get_new_event_id, get_tour_events
from back_end.players import Players
from enumerations import EventType


class ScheduleForm(FlaskForm):
    time = TimeField('Time')
    text = StringField('Item')


class TourScheduleForm(FlaskForm):
    date = DateField('Time')
    venue = SelectField(label='Course', choices=[('', 'Choose course ...')] + get_all_venue_names())


class EventForm(FlaskForm):
    members = Players().get_current_members()
    event = StringField(label='Event')
    date = DateField(label='Date')
    venue = SelectField(label='Venue', choices=[('', 'Choose venue ...')] + get_all_venue_names())
    organiser = SelectField(label='Organiser', choices=[('', 'Choose organiser ...')] + [(m, m) for m in members])
    member_price = DecimalField(label='Member Price')
    guest_price = DecimalField(label='Guest Price')
    start_booking = DateField(label='Booking Starts')
    end_booking = DateField(label='Booking Ends')
    max = IntegerField(label='Maximum')
    event_type = HiddenField(label='Event Type')
    schedule = FieldList(FormField(ScheduleForm))
    tour_schedule = FieldList(FormField(TourScheduleForm))
    directions = TextAreaField(label='Directions', default='')
    note = TextAreaField(label='Notes', default='')
    submit = SubmitField(label='Save')
    editable = HiddenField(label='Editable')

    def populate_event(self, year, event_id, event_type):
        self.editable.data = year >= datetime.date.today().year
        event = get_event(year, event_id)
        self.date.data = event['date']
        self.event.data = event['event']
        self.organiser.data = event['organiser']
        self.member_price.data = event['member_price']
        self.guest_price.data = event['guest_price']
        self.start_booking.data = event['start_booking']
        self.end_booking.data = event['end_booking']
        self.max.data = event['max']
        self.event_type.data = event_type.name
        self.note.data = event['note']
        if event_type in [EventType.wags_vl_event, EventType.non_event]:
            self.venue.data = event['venue']
            self.directions.data = event['directions']
            for item in event['schedule']:
                item_form = ScheduleForm()
                item_form.time = item['time']
                item_form.text = item['text']
                self.schedule.append_entry(item_form)
        if event_type == EventType.wags_tour:
            self.venue.data = ''
            for item in get_tour_events(year, event_id):
                item_form = TourScheduleForm()
                item_form.date = item['date']
                item_form.course = item['venue']
                self.tour_schedule.append_entry(item_form)
        return event_id

    def save_event(self, year, event_id):
        errors = self.errors
        if len(errors) > 0:
            return False
        event = {
            'date': self.date.data,
            'event': self.event.data,
            'organiser': self.organiser.data,
            'member_price': self.member_price.data,
            'guest_price': self.guest_price.data,
            'start_booking': self.start_booking.data,
            'end_booking': self.end_booking.data,
            'max': self.max.data or '0',
            'event_type': self.event_type.data,
            'note': self.note.data,
            'venue': self.venue.data,
            'directions': self.directions.data,
            'schedule': [],
            'tour_schedule': []
        }
        if event_id == "0":
            event_id = str(get_new_event_id(year, event))

        if EventType[self.event_type.data] == EventType.wags_vl_event:
            for item in self.schedule.data:
                event['schedule'].append(item)

        save_event(year, event_id, event)

        if EventType[self.event_type.data] == EventType.wags_tour:
            tour_event_id = int(event_id)
            for item in self.tour_schedule.data:
                if item['date']:
                    tour_event_id += 0.1
                    id = '{0:.1f}'.format(tour_event_id)
                    item.update({
                        'num': id,
                        'event': self.event.data,
                        'event_type': EventType.wags_vl_event.name,
                        'start_booking': None,
                        'end_booking': None,
                        'member_price': None,
                        'guest_price': None,
                        'schedule': [],
                    })
                    event['tour_schedule'].append(item)
                    save_event(year, id, item)

        return True

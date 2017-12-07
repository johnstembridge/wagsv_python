import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, TextAreaField, IntegerField, SubmitField, FieldList, \
    FormField, HiddenField
from wtforms_components import TimeField
from wtforms.fields.html5 import DateField
from interface import get_all_venue_names, get_all_event_types, get_all_event_names, get_event, save_event, \
    get_new_event_id
from back_end.players import Players


class ScheduleForm(FlaskForm):
    time = TimeField('Time')
    text = StringField('Item')


class EventForm(FlaskForm):
    members = Players().get_current_members()
    event = SelectField(label='Event', choices=[('', 'Choose event ...')] + get_all_event_names())
    date = DateField(label='Date')
    venue = SelectField(label='Venue', choices=[('', 'Choose venue ...')] + get_all_venue_names())
    organiser = SelectField(label='Organiser', choices=[('', 'Choose organiser ...')] + [(m, m) for m in members])
    member_price = DecimalField(label='Member Price')
    guest_price = DecimalField(label='Guest Price')
    start_booking = DateField(label='Booking Starts')
    end_booking = DateField(label='Booking Ends')
    max = IntegerField(label='Maximum')
    event_type = SelectField(label='Event Type', choices=[('', 'Choose event type...')] + get_all_event_types())
    schedule = FieldList(FormField(ScheduleForm))
    directions = TextAreaField(label='Directions', default='')
    note = TextAreaField(label='Notes', default='')
    submit = SubmitField(label='Save')
    editable = HiddenField(label='Editable')

    def populate_event(self, year, event_id):
        self.editable.data = year >= datetime.date.today().year
        event = get_event(year, event_id)
        self.date.data = event['date']
        self.event.data = event['event']
        self.venue.data = event['venue']
        self.organiser.data = event['organiser']
        self.member_price.data = event['member_price']
        self.guest_price.data = event['guest_price']
        self.start_booking.data = event['start_booking']
        self.end_booking.data = event['end_booking']
        self.max.data = event['max']
        self.event_type.data = event['event_type']
        self.directions.data = event['directions']
        self.note.data = event['note']
        for item in event['schedule']:
            item_form = ScheduleForm()
            item_form.time = item['time']
            item_form.text = item['text']
            self.schedule.append_entry(item_form)
        return event_id

    def save_event(self, year, event_id):
        errors = self.errors
        if len(errors) > 0:
            return False
        event = {
            'date': self.date.data,
            'event': self.event.data,
            'venue': self.venue.data,
            'organiser': self.organiser.data,
            'member_price': self.member_price.data,
            'guest_price': self.guest_price.data,
            'start_booking': self.start_booking.data,
            'end_booking': self.end_booking.data,
            'max': self.max.data,
            'event_type': self.event_type.data,
            'directions': self.directions.data,
            'note': self.note.data,
            'schedule': []
        }
        for item in self.schedule.data:
            event['schedule'].append(item)

        if event_id == "0":
            event_id = get_new_event_id(year, event)
            pass
        save_event(year, event_id, event)
        return True

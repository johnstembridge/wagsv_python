
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, TextAreaField, IntegerField, SubmitField, FieldList, \
    FormField
from wtforms_components import TimeField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField
from interface import get_all_venue_names, get_all_event_types, get_all_event_names, get_event, save_event
from back_end.players import Players


class ScheduleForm(FlaskForm):
    time = TimeField('Time')
    text = StringField('Item')


class EventForm(FlaskForm):
    members = Players().get_current_members()
    event = SelectField(label='Event', validators=[DataRequired()], choices=[('', 'Choose event ...')] + get_all_event_names())
    date = DateField(label='Date', validators=[DataRequired()])
    venue = SelectField(label='Venue', validators=[DataRequired()], choices=[('', 'Choose venue ...')] + get_all_venue_names())
    organiser = SelectField(label='Organiser', validators=[DataRequired()], choices=[('', 'Choose organiser ...')] + [(m, m) for m in members])
    member_price = DecimalField(label='Member Price', validators=[DataRequired()])
    guest_price = DecimalField(label='Guest Price', validators=[DataRequired()])
    start_booking = DateField(label='Booking Starts', validators=[DataRequired()])
    end_booking = DateField(label='Booking Ends', validators=[DataRequired()])
    max = IntegerField(label='Maximum', validators=[DataRequired()])
    event_type = SelectField(label='Event Type', validators=[DataRequired()], choices=[('', 'Choose event type...')] + get_all_event_types())
    schedule = FieldList(FormField(ScheduleForm))
    directions = TextAreaField(label='Directions', default='')
    note = TextAreaField(label='Notes', default='')
    submit = SubmitField(label='Save')

    def populate_event(self, year, event_id):
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

        save_event(year, event_id, event)
        return True
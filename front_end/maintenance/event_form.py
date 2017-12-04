import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, TextAreaField, IntegerField, SubmitField, FieldList, \
    FormField, HiddenField
from wtforms_components import TimeField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField
from interface import get_all_venue_names, get_all_event_names, get_event, save_event, \
    get_event_list, get_next_event_id, get_results, save_event_scores
from back_end.players import Players


class ScheduleForm(FlaskForm):
    time = TimeField('Time')
    text = StringField('Item')


class EventItemForm(FlaskForm):
    num = IntegerField(label='id')
    date = DateField(label='Date')
    event = StringField(label='Event')
    venue = StringField(label='Venue')


class EventListForm(FlaskForm):
    event_list = FieldList(FormField(EventItemForm))
    add_event = SubmitField(label='Add Event')
    edit_event = SubmitField(label='Edit Event')
    results_event = SubmitField(label='Edit Results')
    editable = HiddenField(label='Editable')

    def populate_event_list(self, year):
        self.editable.data = 'y' if year >= datetime.date.today().year - 1 else 'n'
        for item in get_event_list(year):
            item_form = EventItemForm()
            item_form.num = item['num']
            item_form.date = item['date']
            item_form.event = item['event']
            item_form.venue = item['venue']
            self.event_list.append_entry(item_form)

    def get_next_event_id(self, year):
        return get_next_event_id(year)


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
    schedule = FieldList(FormField(ScheduleForm))
    directions = TextAreaField(label='Directions', default='')
    notes = TextAreaField(label='Notes', default='')
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
        self.directions.data = event['directions']
        self.notes.data = event['notes']
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
            'directions': self.directions.data,
            'notes': self.notes.data,
            'schedule': []
        }
        # event['max'] = form.max.data
        for item in self.schedule.data:
            event['schedule'].append(item)

        save_event(year, event_id, event)
        return True
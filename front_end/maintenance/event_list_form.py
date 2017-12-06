import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FieldList, \
    FormField, HiddenField
from wtforms.fields.html5 import DateField
from interface import get_event_list, get_next_event_id


class EventItemForm(FlaskForm):
    num = IntegerField(label='id')
    date = DateField(label='Date')
    event = StringField(label='Event')
    venue = StringField(label='Venue')
    event_type = HiddenField(label='Event type')


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
            item_form.event_type = item['type']
            self.event_list.append_entry(item_form)

    def get_next_event_id(self, year):
        return get_next_event_id(year)

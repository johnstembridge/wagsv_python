import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FieldList, FormField, HiddenField
from wtforms.fields.html5 import DateField
from interface import get_event_list


class EventItemForm(FlaskForm):
    num = StringField(label='id')
    date = DateField(label='Date')
    event = StringField(label='Event')
    venue = StringField(label='Venue')
    event_type = HiddenField(label='Event type')


class EventListForm(FlaskForm):
    event_list = FieldList(FormField(EventItemForm))
    add_event = SubmitField(label='Add Event')
    add_tour = SubmitField(label='Add Tour')
    add_non = SubmitField(label='Add Non Event')
    editable = HiddenField(label='Editable')

    def populate_event_list(self, year):
        self.editable.data = year >= datetime.date.today().year
        for item in get_event_list(year):
            item_form = EventItemForm()
            item_form.num = item['num']
            item_form.date = item['date']
            item_form.event = item['event']
            item_form.venue = item['venue']
            item_form.event_type = item['type']
            self.event_list.append_entry(item_form)


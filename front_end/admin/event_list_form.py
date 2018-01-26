import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FieldList, FormField, HiddenField
from wtforms.fields.html5 import DateField
from back_end.interface import get_event_list, is_event_editable


class EventItemForm(FlaskForm):
    num = StringField(label='id')
    date = DateField(label='Date')
    event = StringField(label='Event')
    venue = StringField(label='Venue')
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
        for item in get_event_list(year):
            item_form = EventItemForm()
            item_form.num = item['num']
            item_form.date = item['date']
            item_form.event = item['event']
            item_form.venue = item['venue']
            item_form.event_type = item['type']
            item_form.result = item['date'] < datetime.date.today()
            self.event_list.append_entry(item_form)


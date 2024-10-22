import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, FieldList, FormField, HiddenField, SelectField, SubmitField
from wtforms.fields.html5 import DateField
from back_end.data_utilities import encode_date_short
from front_end.form_helpers import set_select_field
from globals.config import url_for_user
from globals.enumerations import EventType, HandicapRegime
from back_end.interface import get_venue_url, get_event_select_list, get_events_for_year


class EventItemForm(FlaskForm):
    num = HiddenField(label='id')
    date = DateField(label='Date')
    event = StringField(label='Event')
    trophy_id = HiddenField(label='Trophy id')
    venue_url = StringField(label='Link to Venue')
    venue = StringField(label='Venue')
    slope = StringField(label='Slope')
    par = StringField(label='Par')
    rating = StringField(label='Rating')
    event_type = HiddenField(label='Event type')
    bookable = HiddenField(label='Event bookable')
    result = HiddenField(label='Result available')
    new_section = HiddenField(label='Start new section')


class EventListForm(FlaskForm):
    event_list = FieldList(FormField(EventItemForm))
    handicap_regime = HiddenField(label='Wags handicap version')

    def populate_event_list(self, year):
        self.handicap_regime.data = HandicapRegime.for_year(year)
        first = True
        for event in get_events_for_year(year):
            cd = event.course.course_data_as_of(year) if event.course else None
            event_type = event.type
            item_form = EventItemForm()
            item_form.num = event.id
            item_form.date = encode_date_short(event.date)
            if event.trophy:
                item_form.event = event.trophy.name
                item_form.trophy_id = event.trophy.id
            else:
                item_form.event = event.venue.name
                item_form.trophy_id = None
            item_form.venue = event.venue.name
            item_form.venue_url = get_venue_url(event.venue)
            if event.course:
                item_form.slope = cd.slope
                if HandicapRegime.for_year(year) == HandicapRegime.wags3:
                    item_form.par = cd.course_par()
                    item_form.rating = cd.rating
            else:
                item_form.slope = item_form.par = item_form.rating = ''
            item_form.event_type = event_type.name
            item_form.new_section = not (first or event.tour_event_id)
            first = False
            item_form.bookable = event.is_bookable()
            item_form.result = event.date < datetime.date.today() and event.type in \
                (EventType.wags_vl_event, EventType.wags_tour, EventType.minotaur)
            self.event_list.append_entry(item_form)


class EventSelectForm(FlaskForm):
    event = SelectField(label='Select Event', coerce=int)
    show_result = SubmitField(label='Show Result')

    def populate_event_select(self):
        set_select_field(self.event, get_event_select_list(), item_name='Event')

    def show_event_result(self):
        event_id = self.event.data
        return url_for_user('results_event', event_id=event_id)

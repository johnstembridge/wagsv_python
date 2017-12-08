from flask import render_template, redirect, url_for, flash
from event_list_form import EventListForm
from event_details_form import EventForm
from event_result_form import EventResultsForm
from event_handicap_form import EventHandicapsForm
from event_card_form import EventCardForm
from handicap_history_form import HandicapHistoryForm
from utility import render_link
from enumerations import EventType


class MaintainVenues:

    @staticmethod
    def list_venues(year):
        # form = EventListForm()
        # if form.is_submitted():
        #     if form.add_event.data:
        #         event_type = EventType.wags_vl_event.name
        #     if form.add_tour.data:
        #         event_type = EventType.wags_tour.name
        #     if form.add_non.data:
        #         event_type = EventType.non_event.name
        #     return redirect(url_for('edit_event', year=year, event_id=0, event_type=event_type))
        # form.populate_event_list(int(year))
        #
        # return render_template('event_list.html', form=form, year=year, render_link=render_link)
        return '<h1>List venues</h1>'

    @staticmethod
    def edit_venue(year, venue_id):
        # form = EventForm()
        # if form.is_submitted():
        #     if form.save_event(int(year), event_id):
        #         flash('Event saved', 'success')
        # if not form.is_submitted():
        #     form.populate_event(int(year), event_id, event_type)
        return '<h1>Edit venue {} {}</h1>'.format(venue_id, year)


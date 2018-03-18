from flask import render_template, redirect, flash

from .event_card_form import EventCardForm
from .event_details_form import EventForm
from .event_handicap_form import EventHandicapsForm
from .event_list_form import EventListForm
from .event_result_form import EventResultsForm
from .handicap_history_form import HandicapHistoryForm
from .tour_result_form import TourResultsForm
from globals.enumerations import EventType
from globals.config import url_for_admin
from front_end.utility import render_link


class MaintainEvents:

    @staticmethod
    def list_events(year):
        form = EventListForm()
        if form.is_submitted():
            if form.add_event.data:
                event_type = EventType.wags_vl_event.name
            if form.add_tour.data:
                event_type = EventType.wags_tour.name
            if form.add_non.data:
                event_type = EventType.non_event.name
            return redirect(url_for_admin('edit_event', year=year, event_id=0, event_type=event_type))
        form.populate_event_list(int(year))

        return render_template('admin/event_list.html', form=form, year=year, render_link=render_link, EventType=EventType)

    @staticmethod
    def edit_event(year, event_id, event_type=None):
        if event_type:
            event_type = EventType[event_type]
        else:
            event_type = EventType.wags_vl_event
        form = EventForm()
        if form.is_submitted():
            if form.save_event(int(year), event_id):
                flash('Event saved', 'success')
                return redirect(url_for_admin('events_main'))
        else:
            form.populate_event(int(year), event_id, event_type)
        event = event_id if event_id != "0" else "(new)"
        if event_type == EventType.wags_vl_event:
            return render_template('admin/event_details.html', form=form, event_id=event, year=year)
        if event_type == EventType.wags_tour:
            return render_template('admin/tour_details.html', form=form, event_id=event, year=year)
        if event_type == EventType.non_event:
            return render_template('admin/non_event_details.html', form=form, event_id=event, year=year)

    @staticmethod
    def results_event(year, event_id, event_type=None):
        if event_type:
            event_type = EventType(int(event_type))
        else:
            event_type = EventType.wags_vl_event
        if event_type == EventType.wags_vl_event:
            return MaintainEvents.results_vl_event(year, event_id)
        if event_type == EventType.wags_tour:
            return MaintainEvents.results_tour_event(year, event_id)

    @staticmethod
    def results_vl_event(year, event_id):
        form = EventResultsForm()
        if form.is_submitted():
            if form.save_results.data:
                if form.save_event_results(year, event_id):
                    flash('results saved', 'success')
                    return redirect(url_for_admin('results_event', year=year, event_id=event_id))
            if form.add_player.data:
                return redirect(url_for_admin('results_event', year=year, event_id=event_id))
        else:
            form.populate_event_results(int(year), event_id)
        return render_template('admin/event_result.html', form=form, event=year + event_id, render_link=render_link)

    @staticmethod
    def results_tour_event(year, event_id):
        form = TourResultsForm()
        form.populate_event_results(int(year), event_id)
        return render_template('admin/tour_result.html', form=form, event=year + event_id, render_link=render_link)

    @staticmethod
    def handicaps_event(year, event_id):
        form = EventHandicapsForm()
        if form.is_submitted():
            if form.save_handicaps.data:
                if form.save_event_handicaps():
                    flash('Handicaps saved', 'success')
                    return redirect(url_for_admin('handicaps_event', year=year, event_id=event_id))
        else:
            form.populate_event_handicaps(int(year), event_id)
        return render_template('admin/event_handicap.html', form=form, event=year + event_id, render_link=render_link)

    @staticmethod
    def card_event_player(year, event_id, player_id):
        form = EventCardForm()
        if form.is_submitted():
            if form.save_card.data:
                if form.save_event_card(year, event_id, player_id, form):
                    flash('Card saved', 'success')
                    return redirect(url_for_admin('results_event', year=year, event_id=event_id))
        else:
            form.populate_card(year, event_id, player_id)
        return render_template('admin/event_card.html', form=form, event=year + event_id, render_link=render_link)

    @staticmethod
    def handicap_history_player(year, event_id, player_id):
        form = HandicapHistoryForm()
        form.populate_history(year, event_id, player_id)
        return render_template('admin/handicap_history.html', form=form)


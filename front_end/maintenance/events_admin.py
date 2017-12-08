from flask import render_template, redirect, url_for, flash
from event_list_form import EventListForm
from event_details_form import EventForm
from event_result_form import EventResultsForm
from event_handicap_form import EventHandicapsForm
from event_card_form import EventCardForm
from handicap_history_form import HandicapHistoryForm
from utility import render_link
from enumerations import EventType


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
            return redirect(url_for('edit_event', year=year, event_id=0, event_type=event_type))
        form.populate_event_list(int(year))

        return render_template('event_list.html', form=form, year=year, render_link=render_link)

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
        if not form.is_submitted():
            form.populate_event(int(year), event_id, event_type)
        event = event_id if event_id != "0" else "(new)"
        return render_template('event_details.html', form=form, event_id=event, year=year)

    @staticmethod
    def results_event(year, event_id):
        form = EventResultsForm()
        if form.is_submitted():
            if form.save_results.data:
                if form.save_event_results(year, event_id):
                    flash('results saved', 'success')
                    return redirect(url_for('results_event', year=year, event_id=event_id))
        else:
            form.populate_event_results(int(year), event_id)
        return render_template('event_result.html', form=form, event=year + event_id, render_link=render_link)

    @staticmethod
    def handicaps_event(year, event_id):
        form = EventHandicapsForm()
        if form.is_submitted():
            if form.save_handicaps.data:
                if form.save_event_handicaps(year, event_id):
                    flash('Handicaps saved', 'success')
                    return redirect(url_for('handicaps_event', year=year, event_id=event_id))
        else:
            form.populate_event_handicaps(int(year), event_id)
        return render_template('event_handicap.html', form=form, event=year + event_id, render_link=render_link)

    @staticmethod
    def card_event_player(year, event_id, player_id):
        form = EventCardForm()
        if form.is_submitted():
            if form.save_card.data:
                if form.save_event_card(year, event_id, player_id, form):
                    flash('Card saved', 'success')
                    return redirect(url_for('results_event', year=year, event_id=event_id))
        else:
            form.populate_card(year, event_id, player_id)
        return render_template('event_card.html', form=form, event=year + event_id, render_link=render_link)

    @staticmethod
    def handicap_history_player(year, event_id, player_id):
        form = HandicapHistoryForm()
        form.populate_history(year, event_id, player_id)
        return render_template('handicap_history.html', form=form)


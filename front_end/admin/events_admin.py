import os
from flask import render_template, redirect, flash

from back_end.data_utilities import fmt_date, coerce
from back_end.interface import get_event
from back_end.file_access import get_file_contents, write_file
from .event_add_player_form import AddPlayerForm
from .event_report_form import EventReportForm
from .event_card_form import EventCardForm
from .event_details_form import EventForm
from .event_bookings_form import EventBookingsForm
from .event_handicap_form import EventHandicapsForm
from .event_list_form import EventListForm, EventCalendarListForm
from .event_result_form import EventResultsForm
from .handicap_history_form import HandicapHistoryForm
from globals.enumerations import EventType
from globals.config import url_for_admin
from globals import config
from front_end.form_helpers import render_link, render_html


class MaintainEvents:

    @staticmethod
    def list_events(year):
        form = EventListForm()
        if form.is_submitted():
            if form.publish_calendar.data:
                return redirect(url_for_admin('events_calendar', year=year))
            if form.add_event.data:
                event_type = EventType.wags_vl_event.value
            if form.add_tour.data:
                event_type = EventType.wags_tour.value
            if form.add_non_vl.data:
                event_type = EventType.non_vl_event.value
            if form.add_non.data:
                event_type = EventType.non_event.value
            return redirect(url_for_admin('edit_event', event_id=0, event_type=event_type))
        form.populate_event_list(int(year))

        return render_template('admin/event_list.html', form=form, render_link=render_link, EventType=EventType,
                               year=year)

    @staticmethod
    def events_calendar(year):
        form = EventCalendarListForm()
        form.populate_calendar_event_list(int(year))
        csv = render_template('admin/event_calendar.txt', event_calendar_list=form.event_calendar_list)
        csv = csv.replace('\n\n', '\n').replace('\n\n', '\n')
        file = os.path.join(config.get('locations')['output'], 'calendar_' + str(year) + '.csv')
        write_file(file, csv)
        flash('Calendar published as ' + file, 'success')
        return redirect(url_for_admin('list_events', year=year))

    @staticmethod
    def edit_event(event_id, event_type):
        form = EventForm()

        if form.is_submitted():
            if form.validate_on_submit():
                if form.save_event(event_id):
                    flash('Event saved', 'success')
                    year = form.date.data.year
                    return redirect(url_for_admin('list_events', year=year))
            else:
                form.populate_choices(event_id, event_type)
                event_type = EventType(coerce(form.event_type.data, int))
        else:
            form.populate_event(event_id, event_type)
            event_type = EventType(coerce(form.event_type.data, int))
        event = event_id if event_id != 0 else "(new)"
        event_type_desc = event_type.long_description()
        if event_type in [EventType.wags_vl_event, EventType.non_vl_event, EventType.cancelled]:
            return render_template('admin/event_details.html', form=form, event_id=event,
                                   event_type_desc=event_type_desc)
        if event_type in [EventType.wags_tour, EventType.minotaur]:
            return render_template('admin/tour_details.html', form=form, event_id=event,
                                   event_type_desc=event_type_desc)
        if event_type == EventType.non_event:
            return render_template('admin/non_event_details.html', form=form, event_id=event,
                                   event_type_desc=event_type_desc)

    @staticmethod
    def event_bookings(event_id):
        form = EventBookingsForm()
        if form.is_submitted():
            if form.validate_on_submit():
                if form.save_bookings.data:
                    if form.save_event_bookings(event_id):
                        flash('Bookings saved', 'success')
                        year = (get_event(event_id).date).year
                        return redirect(url_for_admin('list_events', year=year))
                if form.add_player.data:
                    return redirect(url_for_admin('add_player_to_event', event_id=event_id))
            else:
                form.populate_event_bookings(event_id)
        else:
            form.populate_event_bookings(event_id)
        return render_template('admin/event_bookings.html', form=form, event_id=event_id)

    @staticmethod
    def results_vl_event(event_id):
        form = EventResultsForm()
        if form.is_submitted():
            if form.save_results.data:
                if form.save_event_results(event_id):
                    flash('results saved', 'success')
                    return redirect(url_for_admin('results_event', event_id=event_id))
            if form.add_player.data:
                return redirect(url_for_admin('add_player_to_event', event_id=event_id))
        else:
            form.populate_event_results(event_id)
        return render_template('admin/event_result.html', form=form, event=event_id, render_link=render_link)

    @staticmethod
    def handicaps_event(event_id):
        form = EventHandicapsForm()
        if form.is_submitted():
            if form.save_handicaps.data:
                if form.save_event_handicaps(event_id):
                    flash('Handicaps saved', 'success')
                    return redirect(url_for_admin('handicaps_event', event_id=event_id))
        else:
            form.populate_event_handicaps(event_id)
        return render_template('admin/event_handicap.html', form=form, event_id=event_id, render_link=render_link)

    @staticmethod
    def card_event_player(event_id, player_id, position='0', handicap=0, status=''):
        form = EventCardForm()
        if form.is_submitted():
            if form.save_card.data:
                if form.save_event_card(event_id, player_id, form):
                    flash('Card saved', 'success')
                    return redirect(url_for_admin('results_event', event_id=event_id))
        else:
            form.populate_card(event_id, player_id, position, handicap, status)
        return render_template('admin/event_card.html', form=form, event=event_id, render_link=render_link)

    @staticmethod
    def handicap_history_player(event_id, player_id):
        form = HandicapHistoryForm()
        form.populate_history(event_id, player_id)
        return render_template('admin/handicap_history.html', form=form)

    @staticmethod
    def report_event(event_id):
        event = get_event(event_id)
        form = EventReportForm()
        if form.is_submitted():
            if form.save:
                template = os.path.join(config.get('locations')['static'], 'event_report.htm')
                MaintainEvents.save_report_page(template, event, form)
                flash('report saved', 'success')
                return redirect(url_for_admin('list_events', year=event.date.year))
        else:
            report_file = MaintainEvents.report_file_name(event.date)
            if not form.populate_event_report(event_id, report_file):
                flash('Results not yet available', 'warning')
                return redirect(url_for_admin('events_main', event_id=event_id))
        return render_template('admin/event_report.html', form=form, event=event_id)

    @staticmethod
    def save_report_page(template_name, event, form):
        title = event.full_name()
        html = render_html(get_file_contents(template_name),
                           title=title,
                           winner=form.winner_return.data,
                           ld=form.ld.data,
                           ntp=form.ntp.data,
                           report=form.report.data,
                           year=str(event.date.year)
                           )
        file_name = MaintainEvents.report_file_name(event.date)
        write_file(file_name, html, access_all=True)

    @staticmethod
    def report_file_name(event_date):
        date = fmt_date(event_date)
        location = config.get('locations')['reports']
        page_name = 'rp{}.htm'.format(date.replace('/', '')[2:])
        file_name = os.path.join(location, str(event_date.year), page_name)
        return file_name

    @staticmethod
    def add_player_to_event(event_id):
        form = AddPlayerForm()
        if form.is_submitted():
            if form.submit.data:
                if form.add_booking(event_id):
                    return redirect(url_for_admin('bookings_event', event_id=event_id))
                else:
                    return redirect(url_for_admin('add_player_to_event', event_id=event_id))
        else:
            form.populate_add_player(event_id)
        return render_template('admin/event_add_player.html', form=form, event=event_id)

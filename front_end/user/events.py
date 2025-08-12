from flask import render_template, redirect, flash

from front_end.user.event_bookings_form import EventBookingsForm
from front_end.user.event_details_form import EventDetailsForm, EventBookingConfirmationForm
from front_end.user.fixture_card_list_form import FixtureCardListForm
from .event_card_form import EventCardForm
from .event_list_form import EventListForm, EventSelectForm
from .event_result_form import EventResultsForm
from .tour_result_form import TourResultsForm
from front_end.form_helpers import render_link, flash_errors
from back_end.interface import get_event
from globals.enumerations import EventType, HandicapRegime
from globals.config import url_for_html, url_for_user
from datetime import datetime


class ReportEvents:

    @staticmethod
    def list_fixture_cards():
        form = FixtureCardListForm()
        form.populate_card_list()
        return render_template(
            'user/fixture_card_list.html',
            form=form,
            render_link=render_link,
            url_for_user=url_for_user
        )

    @staticmethod
    def list_events(year):
        form = EventListForm()
        form.populate_event_list(year)
        book_or_view = 'Book' if year == datetime.today().year else 'View'
        return render_template(
            'user/event_list.html',
            form=form,
            year=year,
            book_or_view=book_or_view,
            render_link=render_link,
            HandicapRegime = HandicapRegime,
            url_for_user=url_for_user
        )

    @staticmethod
    def select_event():
        form = EventSelectForm()
        if form.is_submitted():
            if form.show_result.data:
                return redirect(form.show_event_result())
        form.populate_event_select()
        return render_template('user/event_select.html', form=form)

    @staticmethod
    def show_or_book_event(event_id, member_id):
        form = EventDetailsForm()
        if member_id > 0:
            if form.validate_on_submit():
                booking = form.book_event(event_id, member_id)
                if booking:
                    flash('Booking saved', 'success')
                    form = EventBookingConfirmationForm()
                    form.populate(booking.title, booking.message)
                    return render_template('user/event_booking_confirmation.html', form=booking)
            elif form.errors:
                flash_errors(form)
            if not form.is_submitted():
                form.populate_event(event_id, member_id)
        return render_template('user/event_details.html', form=form, render_link=render_link, url_for_html=url_for_html, url_for_user=url_for_user)

    @staticmethod
    def show_all_bookings(event_id):
        form = EventBookingsForm()
        form.populate_event_bookings(event_id)
        return render_template('user/event_bookings.html', form=form, render_link=render_link)

    @staticmethod
    def results_event(event_id):
        event_type = get_event(event_id).type
        if event_type == EventType.wags_vl_event:
            return ReportEvents.results_vl_event(event_id)
        if event_type in [EventType.wags_tour, EventType.minotaur]:
            return ReportEvents.results_tour_event(event_id)

    @staticmethod
    def report_event(event_id):
        date = get_event(event_id).date
        year = str(date.year)
        file = 'rp{}.htm'.format(date.strftime('%y%m%d'))
        return redirect(url_for_html('reports', year, file))

    @staticmethod
    def results_vl_event(event_id):
        form = EventResultsForm()
        form.populate_event_results(event_id)
        return render_template('user/event_result.html', form=form, render_link=render_link, url_for_user=url_for_user)

    @staticmethod
    def results_tour_event(event_id):
        form = TourResultsForm()
        form.populate_tour_results(event_id)
        return render_template('user/tour_result.html', form=form, event=event_id, render_link=render_link)

    @staticmethod
    def card_event_player(event_id, player_id):
        form = EventCardForm()
        form.populate_card(event_id, player_id)
        return render_template('user/event_card.html', form=form, render_link=render_link)

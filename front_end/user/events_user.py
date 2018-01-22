from flask import render_template, redirect

from .event_card_form import EventCardForm
from .event_list_form import EventListForm
from .event_result_form import EventResultsForm
from globals.enumerations import EventType
from globals.config import url_for_old_site, url_for_old_service
from .handicap_history_form import HandicapHistoryForm
from .tour_result_form import TourResultsForm
from front_end.utility import render_link
from back_end.interface import get_event


class ReportEvents:

    @staticmethod
    def list_events(year):
        form = EventListForm()
        form.populate_event_list(int(year))
        return render_template('user/event_list.html', form=form, year=int(year), render_link=render_link)

    @staticmethod
    def book_event(year, event_id, event_type=None):
        return redirect(url_for_old_service('services.pl?show_event={}&year={}&book=1'.format(event_id, year)))

    @staticmethod
    def show_event(year, event_id, event_type=None):
        return redirect(url_for_old_service('services.pl?show_event={}&year={}&book=3'.format(event_id, year)))

    @staticmethod
    def results_event(year, event_id, event_type=None):
        if event_type:
            event_type = EventType[event_type]
        else:
            event_type = EventType.wags_vl_event
        if event_type == EventType.wags_vl_event:
            return ReportEvents.results_vl_event(year, event_id)
        if event_type == EventType.wags_tour:
            return ReportEvents.results_tour_event(year, event_id)

    @staticmethod
    def report_event(year, event_id, event_type=None):
        date = get_event(year, event_id)['date']
        file = 'rp{}.htm'.format(date.strftime('%y%m%d'))
        return redirect(url_for_old_site('{}/{}'.format(year, file)))

    @staticmethod
    def results_vl_event(year, event_id):
        form = EventResultsForm()
        form.populate_event_results(int(year), event_id)
        return render_template('user/event_result.html', form=form, event=year + event_id, render_link=render_link)

    @staticmethod
    def results_tour_event(year, event_id):
        form = TourResultsForm()
        form.populate_tour_results(int(year), event_id)
        return render_template('user/tour_result.html', form=form, event=year + event_id, render_link=render_link)

    @staticmethod
    def card_event_player(year, event_id, player_id):
        form = EventCardForm()
        form.populate_card(year, event_id, player_id)
        return render_template('user/event_card.html', form=form, event=year + event_id, render_link=render_link)

    @staticmethod
    def handicap_history_player(year, event_id, player_id):
        form = HandicapHistoryForm()
        form.populate_history(year, event_id, player_id)
        return render_template('user/handicap_history.html', form=form)

    @staticmethod
    def page_not_found(e):
        return render_template('user/404.html'), 404

    @staticmethod
    def internal_error(e):
        return render_template('user/500.html'), 500
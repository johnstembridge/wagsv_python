from flask import render_template, redirect

from .event_card_form import EventCardForm
from .event_list_form import EventListForm
from .event_result_form import EventResultsForm
from globals.enumerations import EventType
from globals.config import url_for_old_site, url_for_old_service
from .handicap_history_form import HandicapHistoryForm
from .player_history_form import PlayerHistoryForm
from .tour_result_form import TourResultsForm
from front_end.utility import render_link
from back_end.interface import get_event, event_date, get_event_by_year_and_name
from back_end.data_utilities import parse_date


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

    @classmethod
    def show_from_date_and_name(cls, date, event_name):
        year = parse_date(date).year
        event_id = get_event_by_year_and_name(year, event_name)['num']
        event_type = None
        return cls.results_event(year, event_id, event_type)

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
        return render_template('user/event_result.html', form=form, event=str(year) + event_id, render_link=render_link)

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
        date = event_date(year, event_id)
        form.populate_history(player_id, date)
        return render_template('user/handicap_history.html', form=form)

    @staticmethod
    def show_playing_history(player_id, year):
        form = PlayerHistoryForm()
        form.populate_history(player_id, year)
        return render_template('user/player_history.html', form=form)
        #return redirect(url_for_old_service('services.pl?playhist=show'))

    @staticmethod
    def page_not_found(e):
        return render_template('user/404.html'), 404

    @staticmethod
    def internal_error(e):
        return render_template('user/500.html'), 500


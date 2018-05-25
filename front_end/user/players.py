from flask import render_template

from .handicap_history_form import HandicapHistoryForm
from .player_history_form import PlayerHistoryForm, SummaryHistoryForm
from back_end.interface import event_date


class ReportPlayers:

    @staticmethod
    def handicap_history_player(event_id, player_id):
        form = HandicapHistoryForm()
        form.populate_history(player_id, event_id)
        return render_template('user/handicap_history.html', form=form)

    @staticmethod
    def playing_history_player(player_id, year=None):
        form = PlayerHistoryForm()
        form.populate_history(player_id, year)
        return render_template('user/player_history.html', form=form)

    @staticmethod
    def playing_history_summary():
        form = SummaryHistoryForm()
        form.populate_summary_history()
        return render_template('user/summary_history.html', form=form)
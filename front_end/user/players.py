from flask import render_template

from front_end.form_helpers import render_link
from .player_history_form import PlayerHistoryForm, SummaryHistoryForm


class ReportPlayers:

    @staticmethod
    def playing_history_player(player_id, year=None):
        form = PlayerHistoryForm()
        form.populate_history(player_id, year)
        return render_template('user/player_history.html', form=form)

    @staticmethod
    def playing_history_summary():
        form = SummaryHistoryForm()
        form.populate_summary_history()
        return render_template('user/summary_history.html', form=form, render_link=render_link)
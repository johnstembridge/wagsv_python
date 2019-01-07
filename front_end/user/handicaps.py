import datetime
from flask import render_template

from .handicaps_form import HandicapsForm
from .handicap_history_form import HandicapHistoryForm
from front_end.form_helpers import render_link
from globals.config import url_for_user

class Handicaps:

    @staticmethod
    def list_handicaps():
        form = HandicapsForm()
        form.populate_handicaps()
        return render_template('user/handicaps.html', form=form, render_link=render_link, url_for_user=url_for_user)

    @staticmethod
    def handicap_history_player(player_id):
        form = HandicapHistoryForm()
        date = datetime.date.today()
        form.populate_history(player_id, date)
        return render_template('user/handicap_history.html', form=form, render_link=render_link, url_for_user=url_for_user)
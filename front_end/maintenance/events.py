from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf import CSRFProtect
from flask_bootstrap import Bootstrap
from event_list_form import EventListForm
from event_form import EventForm
from event_result_form import EventResultsForm
from event_handicap_form import EventHandicapsForm
from event_card_form import EventCardForm
from handicap_history_form import HandicapHistoryForm
from utility import render_link

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret squirrel'
csrf = CSRFProtect(app)

bootstrap = Bootstrap(app)


class MaintainEvents:

    @staticmethod
    @app.route('/events/<year>', methods=['GET', 'POST'])
    def list_events(year):
        form = EventListForm()
        if form.is_submitted():
            if form.add_event.data:
                event_id = form.get_next_event_id(year)
                return redirect(url_for('edit_event', year=year, event_id=event_id))
        form.populate_event_list(int(year))

        return render_template('event_list.html', form=form, year=year, render_link=render_link)

    @staticmethod
    @app.route('/events/<year>/<event_id>', methods=['GET', 'POST'])
    def edit_event(year, event_id):
        form = EventForm()
        if form.validate_on_submit():
            if form.save_event(int(year), event_id):
                flash('Event saved', 'success')
        if not form.is_submitted():
            form.populate_event(int(year), event_id)
        return render_template('event.html', form=form, event_id=event_id, year=year)

    @staticmethod
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @staticmethod
    @app.route('/events/<year>/<event_id>/results', methods=['GET', 'POST'])
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
    @app.route('/events/<year>/<event_id>/handicaps', methods=['GET', 'POST'])
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
    @app.route('/events/<year>/<event_id>/<player_id>/card', methods=['GET', 'POST'])
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
    @app.route('/events/<year>/<event_id>/<player_id>/handicap', methods=['GET', 'POST'])
    def handicap_history_player(year, event_id, player_id):
        form = HandicapHistoryForm()
        form.populate_history(year, event_id, player_id)
        return render_template('handicap_history.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)

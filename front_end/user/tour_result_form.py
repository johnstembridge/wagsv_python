from flask_wtf import FlaskForm
from wtforms import StringField, FieldList, FormField

from back_end.interface import get_event, get_player_names_as_dict, get_tour_results


class TourEventScoreItemForm(FlaskForm):
    points = StringField(label='Points')


class TourEventVenueItemForm(FlaskForm):
    name = StringField(label='Name')


class TourResultItemForm(FlaskForm):
    position = StringField(label='Position')
    player = StringField(label='Player')
    total = StringField(label='Total')
    venue_scores = FieldList(FormField(TourEventScoreItemForm))


class TourResultsForm(FlaskForm):
    event_name = StringField(label='event_name')
    venues = FieldList(FormField(TourEventVenueItemForm))
    scores = FieldList(FormField(TourResultItemForm))

    def populate_tour_results(self, event_id):
        event = get_event(event_id)
        self.event_name.data = event.full_name()
        venues = event.tour_events
        for venue in venues:
            venue_form = TourEventVenueItemForm()
            venue_form.name = venue.course.full_name()
            self.venues.append_entry(venue_form)

        results = get_tour_results(event)
        player_names = get_player_names_as_dict(results.get_columns('player_id'))

        for res in results.data:
            item_form = TourResultItemForm()
            guest = "" if (res[results.column_index('status')] != 0) else " (guest)"
            item_form.position = res[results.column_index('position')]
            item_form.player = player_names[res[results.column_index('player_id')]] + guest
            item_form.total = res[results.column_index('total')]
            for score in res[results.column_index('scores')]:
                score_form = TourEventScoreItemForm()
                score_form.points = score if score > 0 else ''
                item_form.venue_scores.append_entry(score_form)
            self.scores.append_entry(item_form)


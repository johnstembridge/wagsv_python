from flask_wtf import FlaskForm
from wtforms import StringField, FieldList, FormField

from back_end.data_utilities import first_or_default
from back_end.interface import get_event, get_player_names_as_dict, get_tour_scores
from back_end.table import Table
from back_end.calc import get_positions


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
            venue_form.name = venue.course.name
            self.venues.append_entry(venue_form)

        results = self.make_tour_results(event)
        player_names = get_player_names_as_dict(results.get_columns('player_id'))

        for res in results.data:
            item_form = TourResultItemForm()
            guest = ""  # if (res[results.column_index('status')] != "0") else " (guest)"
            item_form.position = res[results.column_index('position')]
            item_form.player = player_names[res[results.column_index('player_id')]] + guest
            item_form.total = res[results.column_index('total')]
            for score in res[results.column_index('scores')]:
                score_form = TourEventScoreItemForm()
                score_form.points = score if score > 0 else ''
                item_form.venue_scores.append_entry(score_form)
            self.scores.append_entry(item_form)

    @staticmethod
    def make_tour_results(event):
        trophy = event.trophy
        event_ids = [v.id for v in event.tour_events]
        dates = {v.id: v.date for v in event.tour_events}
        multi = len([v for v in event.tour_events if v.trophy == trophy]) > 0
        scores = Table(*get_tour_scores(event_ids))
        res = []
        for player_id, event_scores in scores.group_by('player'):
            s = [s for s in event_scores]
            missing = list(set(event_ids).difference(set([x[1] for x in s])))  # event ids
            for m in missing:
                s.append([dates[m], m, 0, 0, None])
            s.sort()
            p = [int(x[3]) for x in s]  # points
            if trophy and multi:
                tp = sum([int(x[3]) for x in s if x[4] == trophy])  # total points for trophy
            else:
                tp = sum(p)
            r = (player_id, p, tp)
            res.append(r)
        head = ['player_id', 'scores', 'total']
        res = Table(head, res)
        res.sort(['total'], reverse=True)
        res.add_column('position', get_positions(res.get_columns('total')))
        return res


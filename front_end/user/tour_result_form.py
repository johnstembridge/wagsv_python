from flask_wtf import FlaskForm
from wtforms import StringField, FieldList, FormField
from back_end.interface import get_event, get_tour_scores, get_tour_event_list, get_player_name
from back_end.table import Table
from back_end.data_utilities import fmt_date
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

    def populate_tour_results(self, year, event_id):
        event = get_event(year, event_id)
        self.event_name.data = '{} {} {}'.format(event['event'], event['venue'], event['date'])

        venues = get_tour_event_list(year, event_id)
        for venue in venues:
            venue_form = TourEventVenueItemForm()
            venue_form.name = venue['course']
            self.venues.append_entry(venue_form)

        dates = [fmt_date(v['date']) for v in venues]
        results = self.get_tour_results(year, event_id, dates)

        for res in results.data:
            item_form = TourResultItemForm()
            guest = "" if (res[results.column_index('status')] != "0") else " (guest)"
            item_form.position = res[results.column_index('position')]
            item_form.player = get_player_name(res[results.column_index('player_id')]) + guest
            item_form.total = res[results.column_index('total')]
            for score in res[results.column_index('scores')]:
                score_form = TourEventScoreItemForm()
                score_form.points = score
                item_form.venue_scores.append_entry(score_form)
            self.scores.append_entry(item_form)

    @staticmethod
    def get_tour_results(year, event_id, dates):
        scores = Table(*get_tour_scores(year, event_id))
        scores.sort(['player', 'date'])
        res = []
        for player_id, event_scores in scores.groupby('player'):
            s = [s for s in event_scores]
            missing = list(set(dates).difference(set([x[0] for x in s])))
            status = s[0][7]
            for m in missing:
                s.append([m] + 7*['0'])
            s.sort()
            s = [int(x[4]) for x in s]
            r = (player_id, status, s, sum(s))
            res.append(r)
        head = ['player_id', 'status', 'scores', 'total']
        res = Table(head, res)
        res.sort(['total'], reverse=True)
        res.add_column('position', get_positions(res.get_column('total')))
        return res


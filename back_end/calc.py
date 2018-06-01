import itertools
import datetime

from back_end.interface import get_event, lookup_course, get_course_data, get_event_cards, get_scores, \
    get_player_names, get_events_in
from back_end.table import Table
from back_end.data_utilities import coerce, my_round
from globals.enumerations import PlayerStatus, EventType


def get_vl(year):
    scores = get_scores(year=year, status=PlayerStatus.member)
    scores.sort(['player_id', 'date'])
    vl = Table(['player_id', 'points', 'events', 'lowest'],
               [vl_summary(scores.column_index('points'), key, list(values))
                for key, values in scores.group_by('player_id')])
    vl.sort(['points', 'lowest'], reverse=True)
    vl.add_column('position', get_positions(vl.get_columns('points')))
    vl.add_column('name', get_player_names(vl.get_columns('player_id')))
    return vl


def vl_summary(pi, player_id, scores):
    points = [s[pi] for s in scores]
    points = sorted(points, reverse=True)
    top_6 = points[:6]
    return [player_id, sum(top_6), len(top_6), min(top_6)]


def get_positions(scores):
    pos = list(itertools.islice(positions(scores), len(scores)))
    return list(itertools.chain.from_iterable(pos))


def positions(scores):
    c = 1
    for key, values in itertools.groupby(scores):
        n = len(list(values))
        p = str(c)
        if n > 1:
            p = '=' + p
        yield [p] * n
        c += n


def calc_event_positions(event_id, result):
    event = get_event(event_id)
    course_data = get_course_data(event.course_id, event.date.year)
    if 'card' not in result.head:
        cards = get_event_cards(event_id)
    else:
        cards = {pc[0]: pc[1] for pc in result.get_columns(['player_id', 'card']) if pc[1]}
    sort = []
    for row in result.data:
        player = dict(zip(result.head, row))
        player_id = player['player_id']
        player_hcap = my_round(float(player['handicap']))
        if player_id in cards:
            shots = [int(s) for s in cards[player_id]]
            points = calc_stableford_points(player_hcap, shots, course_data.si, course_data.par)
            # countback
            tot = (1e6 * sum(points[-18:])) + (1e4 * sum(points[-9:])) + (1e2 * sum(points[-6:])) + sum(points[-3:])
        else:
            tot = 1e6 * coerce(player['points'], float)
        sort.append(tot)
    result.sort_using(sort, reverse=True)
    position = list(range(1, len(result.data) + 1))
    result.update_column('position', position)
    return result


def calc_stableford_points(player_hcap, player_shots, course_si, course_par):
    free = [free_shots(si, player_hcap) for si in course_si]
    net = [coerce(player_shots[i], int) - free[i] for i in range(18)]
    points = [max(0, 2 + course_par[i] - net[i]) for i in range(18)]
    return points


def free_shots(si, hcap):
    s = 0
    if si <= hcap:
        s += 1
    if hcap > 18:
        if si <= hcap - 18:
            s += 1
    return s


def get_big_swing(year):
    year = coerce(year, int)
    date_range = [datetime.date(year - 1, 1, 1), datetime.date(year, 12, 31)]
    events = get_events_in(date_range)  # date, course
    richmond = lookup_course('The Richmond')
    first_and_last = [e for e in events if e.course_id == richmond]
    if len(first_and_last) == 1:
        first_and_last.append(events[-1])
    events = [e for e in events
              if e.date >= first_and_last[0].date
              and e.date <= first_and_last[1].date
              and e.type == EventType.wags_vl_event]
    header = ['player', 'course', 'date', 'points_out', 'points_in', 'swing']
    swings = []
    for event in events:
        swings.extend(get_swings(event))
    swings = Table(header, swings)
    swings.sort('swing', reverse=True)
    swings.top_n(10)
    swings.add_column('position', get_positions(swings.get_columns('swing')))
    return swings


def get_swings(event):
    course_data = get_course_data(event.course_id, event.date.year)
    course_name = event.course.name
    res = []
    for score in event.scores:
        player = score.player
        state = player.state_as_of(event.date)
        if state.status == PlayerStatus.member:
            points = calc_stableford_points(state.handicap, score.card, course_data.si, course_data.par)
            points_out = sum(points[:9])
            points_in = sum(points[-9:])
            swing = points_in - points_out
            if swing > 0:
                res.append((player.full_name(), course_name, event.date, points_out, points_in, swing))
    return res

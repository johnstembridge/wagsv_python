import itertools
import datetime

from back_end.interface import get_event, lookup_course, get_course_data, get_event_cards, get_scores, \
    get_player_names, get_events_in, get_cards, get_handicaps, get_course_names
from back_end.table import Table
from back_end.data_utilities import coerce, parse_date, my_round
from globals.enumerations import PlayerStatus


def get_vl(year):
    scores = Table(*get_scores(year, PlayerStatus.member))
    scores.sort(['player', 'date'])
    vl = Table(['player', 'points', 'events', 'lowest'],
               [vl_summary(scores.column_index('points'), key, list(values))
                for key, values in scores.groupby('player')])
    vl.sort(['points', 'lowest'], reverse=True)
    vl.add_column('position', get_positions(vl.get_column('points')))
    vl.add_column('name', get_player_names(vl.get_column('player')))
    return vl


def vl_summary(pi, player_id, scores):
    points = [int(s[pi]) for s in scores]
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


def calc_event_positions(year, event_id, data):
    event = get_event(year, event_id)
    course_id = lookup_course(event['venue'])
    course_data = get_course_data(course_id, year)
    holes = [str(i) for i in range(1, 19)]
    si = [int(course_data['si' + h]) for h in holes]
    par = [int(course_data['par' + h]) for h in holes]
    cards = get_event_cards(year, event_id)
    for player in data:
        player_id = player['player_id']
        player_hcap = my_round(float(player['handicap_return']))
        if player_id in cards:
            shots = [int(s) for s in cards[player_id]]
            points = calc_stableford_points(player_hcap, shots, si, par)
            # countback
            tot = (1e6 * sum(points[-18:])) + (1e4 * sum(points[-9:])) + (1e2 * sum(points[-6:])) + sum(points[-3:])
        else:
            tot = 1e6 * player['points']
        player['sort'] = tot
    data = sorted(data, key=lambda player: player['sort'], reverse=True)
    for i in range(len(data)):
        player = data[i]
        player['position'] = i + 1
    return data


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
    events = get_events_in(date_range) # date, course
    richmond = lookup_course('The Richmond')
    first_and_last = [e for e in events if e[1] == richmond]
    if len(first_and_last) == 1:
        first_and_last.append(events[-1])
    events = [e for e in events if e[0] >= first_and_last[0][0] and e[0]<first_and_last[1][0]]
    header = ['player_id', 'course_id', 'date', 'points_out', 'points_in', 'swing']
    swings = []
    for event in events:
        swings.extend(get_swings(event))
    swings = Table(header, swings)
    swings.sort('swing', reverse=True)
    swings.top_n(10)
    swings.add_column('position', get_positions(swings.get_column('swing')))
    swings.add_column('player_name', get_player_names(swings.get_column('player_id')))
    swings.add_column('course_name', get_course_names(swings.get_column('course_id')))
    return swings


def get_swings(event):
    date, course = event
    course_data = get_course_data(course, parse_date(date).year)
    holes = [str(i) for i in range(1, 19)]
    course_si = [int(course_data['si' + h]) for h in holes]
    course_par = [int(course_data['par' + h]) for h in holes]
    scores = get_cards(course, date)
    handicaps = dict(get_handicaps(date, PlayerStatus.member))
    res = []
    for (player_id, shots) in scores.items():
        if player_id in handicaps:
            player_hcap = my_round(float(handicaps[player_id]))
            points = calc_stableford_points(player_hcap, shots, course_si, course_par)
            points_out = sum(points[:9])
            points_in = sum(points[-9:])
            swing = points_in - points_out
            if swing > 0:
                res.append((player_id, course, date, points_out, points_in, swing))
    return res

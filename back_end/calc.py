import itertools

from back_end.interface import get_event, lookup_course, get_course_data, get_event_cards, get_scores, \
    get_player_names
from back_end.table import Table
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
        player_hcap = round(float(player['handicap_return']))
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
    net = [player_shots[i] - free[i] for i in range(18)]
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

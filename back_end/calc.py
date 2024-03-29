import datetime

from back_end.interface import get_event, lookup_course, get_event_cards, get_scores, get_player_names, get_events_in
from back_end.table import Table
from back_end.data_utilities import coerce, my_round, first_or_default, get_positions
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


def calc_event_positions(event_id, result):
    event = get_event(event_id)
    course_data = event.course.course_data_as_of(event.date.year)
    if 'card' not in result.head:
        cards = get_event_cards(event_id)
    else:
        cards = {pc[0]: pc[1] for pc in result.get_columns(['player_id', 'card']) if pc[1]}
    sort = []
    for row in result.data:
        player = dict(zip(result.head, row))
        player_id = int(player['player_id'])
        player_hcap = my_round(float(player['handicap']))
        if player_id in cards and cards[player_id]:
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
    if not player_shots:
        return 18*[0]
    free = [free_shots(si, my_round(player_hcap)) for si in course_si]
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
    if hcap > 36:
        if si <= hcap - 36:
            s += 1
    return s


def handicap_category(handicap):
    if handicap >= 21:
        return 4
    if handicap >= 13:
        return 3
    if handicap >= 6:
        return 2
    if handicap >= 0:
        return 1
    return 0


def competition_scratch_score(event):
    position = 2
    while position != 0:
        candidates = [s for s in event.scores if s.position == position]
        if any([c for c in candidates if c.player.state_as_of(event.date).status == PlayerStatus.member]):
            scratch = first_or_default([c.points for c in candidates], 0) - 1
            position = 0
        else:
            position += 1
    return scratch


def suggested_handicap_change(scratch, handicap, score):
    if handicap > 28 or score == 0:
        return handicap
    handicap = float(handicap)
    cut = add = 0.0
    cat = handicap_category(handicap)
    delta = scratch - score
    if delta < 0:
        cut = delta * cat * 0.1
    else:
        if delta - cat > 0:
            add = 0.1
    new = my_round(min(28.0, handicap + cut + add), 1)
    return new


def get_big_swing(year, as_of=datetime.date.today()):
    date_range = (datetime.date(year - 1, 1, 1), datetime.date(year + 1, 12, 31))
    events = get_events_in(date_range)  # date, course
    if len(events) > 0:
        richmond = lookup_course('The Richmond')
        richmond_events = [e for e in events if e.course_id == richmond]
        first = [e for e in richmond_events if as_of > e.date][-1].date + datetime.timedelta(days=1)
        last = [e for e in richmond_events if as_of <= e.date]
        if len(last) == 0:
            last = [e for e in events if as_of <= e.date]
            if len(last) == 0:
                last = as_of
            else:
                last = last[-1].date
        else:
            last = last[0].date
        events = [e for e in events if e.date >= first and e.date <= last and e.type == EventType.wags_vl_event]
    else:
        first = as_of
    header = ['player', 'course', 'date', 'points_out', 'points_in', 'swing']
    swings = []
    for event in events:
        swings.extend(get_swings(event))
    swings = Table(header, swings)
    swings.sort('swing', reverse=True)
    swings.top_n(10)
    swings.add_column('position', get_positions(swings.get_columns('swing')))
    year_range = [first.year, first.year + 1]
    return year_range, swings


def get_swings(event):
    course_data = event.course.course_data_as_of(event.date.year)
    course_name = event.course.name
    res = []
    for score in event.scores:
        player = score.player
        state = player.state_as_of(event.date)
        if state.status in [PlayerStatus.non_vl, PlayerStatus.member]:
            hcap = state.playing_handicap(event)
            points = calc_stableford_points(hcap, score.card, course_data.si, course_data.par)
            points_out = sum(points[:9])
            points_in = sum(points[-9:])
            swing = points_in - points_out
            if swing > 0:
                res.append((player.full_name(), course_name, event.date, points_out, points_in, swing))
    return res

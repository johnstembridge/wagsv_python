import itertools

from back_end.data_utilities import coerce, my_round, first_or_default
from globals.enumerations import PlayerStatus, HandicapRegime
from globals import config

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


def calc_swings(event, players=None):
    course_data = event.course.course_data_as_of(event.date.year)
    course_name = event.course.name
    res = []
    for score in event.scores:
        player = score.player
        if (not players) or players and player.id in players:
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


def calc_playing_handicap_for_event(handicap, event):
    year = event.date.year
    cd = event.course.course_data_as_of(year)
    slope = cd.slope
    course_par = cd.course_par()
    course_rating = cd.rating
    return calc_playing_handicap(handicap, year, slope, course_par, course_rating)


def calc_playing_handicap(handicap, year, slope, course_par=None, course_rating=None):
    if not course_par:
        course_par = course_rating = 0
    handicap_regime = HandicapRegime.for_year(year)
    hcap = None
    # ToDo: upgrade to match/case when Python version 3.10
    if handicap_regime == HandicapRegime.wags0:
        hcap = handicap                                              # unfactored handicap
    if handicap_regime == HandicapRegime.wags1:
        hcap = apply_slope_factor(handicap, slope)                   # apply slope factor
    if handicap_regime == HandicapRegime.wags2:
        hcap = apply_slope_factor(handicap, slope) * 0.95            # apply slope factor, 95%
    if handicap_regime == HandicapRegime.wags3:
        adj = course_rating - course_par                             # adjust by course par and rating
        hcap = (apply_slope_factor(handicap, slope) + adj) * 0.95    # apply slope factor and adjustment, 95%
    return my_round(min(54, hcap),1)


def handicap_slope_factor(slope=None):
    standard_slope = config.get('standard_slope')
    if not slope:
        slope = standard_slope
    return (slope if slope > 0 else standard_slope) / standard_slope


def apply_slope_factor(handicap_index, slope):
    return float(handicap_index) * float(handicap_slope_factor(slope))


def calc_positions(scores):
    pos = list(itertools.islice(positions(scores), len(scores)))
    return list(itertools.chain.from_iterable(pos))


def positions(scores):
    count = 1
    for key, values in itertools.groupby(scores):
        number_tied = len(list(values))
        position = str(count)
        if number_tied > 1:
            position = '=' + position
        yield [position] * number_tied
        count += number_tied

from back_end.interface import get_event, lookup_course, get_course_data, get_event_card


def calc_event_positions(year, event_id, data):
    event = get_event(year, event_id)
    course_id = lookup_course(event['venue'])
    course_data = get_course_data(course_id, year)
    holes = [str(i) for i in range(1, 19)]
    si = [int(course_data['si'+h]) for h in holes]
    par = [int(course_data['par'+h]) for h in holes]
    for player in data:
        player_id = player['player_id']
        player_hcap = round(float(player['handicap_return']))
        card = get_event_card(year, event_id, player_id)
        if card['1'] is not None:
            shots = [int(card[h]) for h in holes]
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
        if si <= hcap-18:
            s += 1
    return s
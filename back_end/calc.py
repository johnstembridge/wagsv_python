
from back_end.interface import get_event, lookup_course, get_course_data, get_event_card


def calc_event_positions(year, event_id, data):
    total = []
    holes = [str(i) for i in range(1, 19)]
    for player in data:
        id = player['player_id']
        card = get_event_card(year, event_id, id)
        shots = [int(card[h]) for h in holes]
        tot = (1e6 * sum(shots[-18:])) + (1e4 * sum(shots[-9:])) + (100 * sum(shots[-6:])) + sum(shots[-3:])
        total.append(tot)
    return data

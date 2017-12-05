import datetime
import os
from itertools import groupby
from operator import itemgetter
from file_access import get_field, get_record, update_record, get_records, get_file, update_records
from data_utilities import encode_date, encode_price, decode_date, decode_price, decode_time, coerce_date, \
    sort_name_list, lookup, force_list, coerce
from back_end.players import Player, Players
from enumerations import EventType


# region file_paths
#
#  data_location = r'D:\python\wagsv\data'
data_location = r'C:\Users\jstembridge\PycharmProjects\wagsv\data'
events_data = r'{}\events.tab'
bookings_data = r'{}\event{}.csv'
players_data = r'players.tab'
members_data = r'members.csv'
course_data = r'course_data.tab'
courses_data = r'courses.tab'
handicaps_data = r'hcaps.tab'
vl_data = r'victor.tab'
scores_data = r'scores.tab'
shots_data = r'shots.tab'


def events_file(year):
    return os.path.join(data_location, events_data.format(year))


def bookings_file(year, event_id):
    return os.path.join(data_location, bookings_data.format(year, event_id))


def handicaps_file():
    return os.path.join(data_location, handicaps_data)


def vl_file():
    return os.path.join(data_location, vl_data)


def members_file():
    return os.path.join(data_location, members_data)


def courses_file():
    return os.path.join(data_location, courses_data)


def players_file():
    return os.path.join(data_location, players_data)


def course_data_file():
    return os.path.join(data_location, course_data)


def scores_file():
    return os.path.join(data_location, scores_data)


def shots_file():
    return os.path.join(data_location, shots_data)
# endregion


def get_all_event_types():
    return [(e.name, e.name) for e in EventType]


def get_all_event_names():
    return [(e, e) for e in get_field(events_file(2017), 'event')]


def get_all_venue_names():
    return [(v, v) for v in get_field(events_file(2017), 'venue')]


def get_all_courses():
    with open(courses_file()) as f:
        all_courses = f.read().splitlines()
    return all_courses


def get_all_players():
    with open(players_file()) as f:
        all_players = f.read().splitlines()
    return all_players


def get_player_name(player_id):
    return get_all_players()[coerce(player_id, int) - 1]


def get_players(as_of, status=None):
    header, recs = get_handicap_records(as_of, status)
    inx = [1]
    pi = [int(itemgetter(*inx)(r)) - 1 for r in recs]
    players = Players().get_all_players()
    current = itemgetter(*pi)(players)
    return sort_name_list(current)


def get_latest_handicaps():
    players = get_field(vl_file(), 'player')
    header, recs = get_records(handicaps_file(), 'player', players)
    recs.sort(key=lambda tup: (tup[1], tup[0]), reverse=True)
    get_item = itemgetter(1)
    res = [list(value)[0] for key, value in groupby(recs, get_item)]
    inx = [1, 2]
    return [itemgetter(*inx)(r) for r in res]


def get_handicaps(as_of, status=None):
    header, recs = get_handicap_records(as_of, status)
    inx = [1, 2]
    return [itemgetter(*inx)(r) for r in recs]


def get_player_handicap(player_id, as_of):
    player_id = coerce(player_id, str)
    header, recs = get_records(handicaps_file(), 'player', player_id)
    recs = [x for x in recs if x[0] <= as_of]
    recs.sort(key=lambda tup: (tup[1], tup[0]), reverse=True)
    return float(dict(zip(header, recs[0]))['handicap'])


def get_handicap_records(as_of, status=None):
    header, recs = get_file(handicaps_file())
    recs = [x for x in recs if x[0] <= as_of]
    recs.sort(key=lambda tup: (tup[1], tup[0]), reverse=True)  # order by date within player
    get_item = itemgetter(1)
    res = [list(value)[0] for key, value in groupby(recs, get_item)]  # get latest for each player
    if status:
        status = [str(s) for s in force_list(status)]
        res = [x for x in res if x[3] in status]  # select members/guests/ex-members
    return header, res


def get_handicap_history(player_id, as_of):
    player_id = coerce(player_id, str)
    header, recs = get_records(handicaps_file(), 'player', player_id)
    recs = [x for x in recs if x[0] <= as_of]
    recs.sort(key=lambda tup: (tup[1], tup[0]), reverse=True)
    inx = lookup(header, ['date', 'handicap', 'status'])
    res = [itemgetter(*inx)(r) for r in recs]
    return res


def get_results(year, event_id):
    date = event_date(year, event_id)
    all_hcaps = dict(get_handicaps(date))
    all_scores = {v[0]: v[1:] for v in get_event_scores(year, event_id)}  # player: position, points, strokes, handicap
    booked = get_booked_players(year, event_id)  # player: handicap
    event_players = list(set(Players().id_to_name(list(all_scores.keys()))) | set(booked.keys()))
    results = []
    for player in sort_name_list(event_players):
        player_id = str(Players().name_to_id(player))
        guest = player in booked and float(booked[player]) > 0
        if player_id not in all_scores:
            hcap = booked[player] if guest else all_hcaps[player_id]
            all_scores[player_id] = [0, '0', 0, hcap]
        det = all_scores[player_id]
        x = {
                'id': player_id,
                'name': player,
                'handicap': det[3],
                'strokes': int(det[2]),
                'points': int(det[1]),
                'position': det[0],
                'guest': 'guest' if guest else ''
            }
        results.append(x)
    return sorted(results, key=lambda k: k['points'], reverse=True)


def get_event_list(year=2017):
    events = []
    for event_id in get_field(events_file(year), 'num'):
        event = get_event(year, event_id)
        if 'venue' in event:
            events.append(
                {
                    'num': event['num'],
                    'date': event['date'],
                    'venue': event['venue'],
                    'event': event['event'],
                    'type': event['event_type'] if 'event_type' in event else EventType.wags_vl_event.name
                }
            )
    return events


def get_event(year, event_id):
    year = coerce(year, int)
    event_id = coerce(event_id, str)
    data = get_record(events_file(year), 'num', event_id)
    data['schedule'] = decode_schedule(data['schedule'])
    data['date'] = decode_date(data['date'], year)
    data['end_booking'] = data.pop('deadline')
    data['end_booking'] = coerce_date(data['end_booking'], year, data['date'] - datetime.timedelta(days=2))
    data['start_booking'] = data['date'] - datetime.timedelta(days=14)
    data['member_price'] = decode_price(data['member_price'])
    data['guest_price'] = decode_price(data['guest_price'])
    data['event_type'] = EventType(int(data.pop('type'))).name
    return data


def get_event_scores(year, event_id):
    date = event_date(year, event_id)
    course_id = str(event_course_id(year, event_id))
    header, data = get_records(scores_file(), ['date', 'course'], [date, course_id])
    inx = lookup(header, ['player', 'position', 'points', 'strokes', 'handicap'])
    res = [itemgetter(*inx)(r) for r in data]
    return res


def save_event_scores(year, event_id, header, data):
    date = event_date(year, event_id)
    course_id = str(event_course_id(year, event_id))
    update_records(scores_file(), ['date', 'course', 'player'], [date, course_id], header, data)


def update_event_scores(year, event_id, player_id, keys, values):
    date = event_date(year, event_id)
    course_id = str(event_course_id(year, event_id))
    update_records(scores_file(), ['date', 'course', 'player'], [date, course_id, player_id], keys, [values])


def get_course_data(course_id, year):
    course_id = coerce(course_id, str)
    year = coerce(year, int)
    keys, recs = get_records(course_data_file(), 'course', course_id)
    ret = None
    for rec in recs:
        test = dict(zip(keys, rec))
        if int(test['year']) >= int(year):
            ret = test
            break
    return ret


def get_event_card(year, event_id, player_id):
    player_id = coerce(player_id, str)
    date = event_date(year, event_id)
    header, recs = get_records(shots_file(), 'date', date)
    inx = lookup(header, 'player')
    recs = [x for x in recs if x[inx] == player_id]
    if len(recs) == 0:
        recs.append([None] * len(header))
    return dict(zip(header, recs[0]))


def save_event_card(year, event_id, player_id, fields, shots):
    course_id = coerce(event_course_id(year, event_id), str)
    player_id = coerce(player_id, str)
    date = event_date(year, event_id)
    new = dict(zip(['date', 'course', 'player'] + fields, [date, course_id, player_id] + shots))
    update_record(shots_file(), ['date', 'course', 'player'], new)


def save_event(year, event_id, data):
    data['num'] = event_id
    data['schedule'] = encode_schedule(data['schedule'])
    data['date'] = encode_date(data['date'])
    data['deadline'] = encode_date(data['end_booking'])
    data['member_price'] = encode_price(data['member_price'])
    data['guest_price'] = encode_price(data['guest_price'])
    data['start_booking'] = encode_date(data['start_booking'])
    data['type'] = EventType[data['event_type']].value
    data['directions'] = data.pop('directions')
    update_record(events_file(year), 'num', data)


def decode_schedule(sched):
    # schedule is comma delimited set of items,
    # each item in form: hh.mm text  e.g. 10.30 Tee-off 18 holes
    if sched:
        ss = [(t.strip()).split(' ', 1) for t in sched.split(',')]
    else:
        ss = []
    while len(ss) < 6:
        ss.append([None, None])
    return [{'time': decode_time(s[0]), 'text': s[1]} for s in ss]


def encode_schedule(sched):
    # return schedule to external form (see decode_schedule)
    ss = [s for s in sched if (not empty_schedule_item(s))]
    ss = sorted(ss, key=lambda k: k['time'])
    ss = [(s['time'].strftime('%H.%M')) + ' ' + s['text'].replace(',', '').replace(':', '-') for s in ss]
    ss = ','.join(ss)
    return ss


def empty_schedule_item(item):
    return (not item['text']) and item['time'].hour == 0 and item['time'].minute == 0


def get_next_event_id(year):
    ids = [int(m) for m in get_field(events_file(year), 'num')]
    return 1 + max(ids)


def get_booked_players(year, event_id):
    file = bookings_file(year, event_id)
    if not os.path.isfile(file):
        file = bookings_file(year, 0)
    header, bookings = get_records(file, 'playing', '1')
    res = []
    for b in bookings:
        booking = dict(zip(header, b))
        number = int(booking['number'])
        if number > 0:
            name = Player.normalise_name(booking['name'])
            res.append([name, 0])
            count = 1
            while count < number:
                guest_name = Player.normalise_name(booking['guest' + str(count)])
                guest_handicap = booking['guest' + str(count) + '_hcap']
                res.append([guest_name, guest_handicap])
                count += 1
    return {v[0]: v[1] for v in res}


def lookup_course(course):
    return lookup(get_all_courses(), course)


def event_course_id(year, event_id):
    event = get_event(year, event_id)
    course_id = lookup_course(event['venue']) + 1
    return course_id


def event_date(year, event_id):
    event = get_event(year, event_id)
    date = event['date'].strftime('%Y/%m/%d')
    return date


def event_type(year, event_id):
    event = get_event(year, event_id)
    event_type = event['event_type']
    return event_type


def save_hcaps(date, header, data):
    update_records(handicaps_file(), ['date', 'player'], [date], header, data)


def is_latest_event(event_id):
    today = datetime.date.today()
    year = today.year
    events = get_event_list(year)
    nums = [int(e['num']) for e in events if e['date'] <= today]
    if len(nums) > 0:
        return nums[-1] == event_id
    return False

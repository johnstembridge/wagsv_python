import datetime
import math
import os
import sys
from itertools import groupby
from operator import itemgetter
from collections import OrderedDict

from back_end.table import Table
from globals.config import url_for_old_site

from back_end.players import Player, Players
from .data_utilities import encode_date, encode_price, decode_date, decode_price, decode_time, \
    sort_name_list, lookup, force_list, coerce, decode_event_type, encode_event_type, dequote, \
    encode_address, decode_address, de_the, encode_directions, decode_directions, coerce_date, coerce_fmt_date, \
    is_num, to_float, parse_date, decode_date_range, fmt_date
from .file_access import get_field, get_record, update_record, get_records, get_file, update_records, get_fields, \
    create_data_file, get_news_file
from globals import config
from globals.enumerations import EventType, PlayerStatus

# region file_paths

data_location = config.get('locations')['data']
html_location = config.get('locations')['html']
events_data = r'{}/events.tab'
venues_data = r'venue_info.txt'
bookings_data = r'{}/event{}.csv'
players_data = r'players.tab'
members_data = r'members.csv'
course_data = r'course_data.tab'
courses_data = r'courses.txt'
handicaps_data = r'hcaps.tab'
scores_data = r'scores.tab'
shots_data = r'shots.tab'
trophies_data = r'trophies.txt'
admin_users = r'admin_users.txt'
news_data = r'news/news.htm'


def events_file(year):
    return os.path.join(data_location, events_data.format(year))


def events_file_fields():
    return ['num', 'date', 'venue', 'event', 'course', 'address', 'post_code', 'phone', 'member_price', 'guest_price',\
            'schedule', 'organiser', 'directions', 'note', 'dinner_price', 'dinner_incl', 'jacket', 'url', 'deadline',\
            'booking_start', 'max', 'type']


def venues_file():
    return os.path.join(data_location, venues_data)


def bookings_file(year, event_id):
    return os.path.join(data_location, bookings_data.format(year, event_id))


def bookings_file_fields():
    return ['date', 'name', 'playing', 'number', 'cost', 'paid', 'guest1', 'guest1_hcap', 'guest2', 'guest2_hcap',\
            'guest3', 'guest3_hcap', 'comment']


def handicaps_file():
    return os.path.join(data_location, handicaps_data)


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


def trophies_file():
    return os.path.join(data_location, trophies_data)


def news_file():
    return os.path.join(html_location, news_data)


def admin_users_file():
    return os.path.join(data_location, admin_users)
# endregion


# region venues
def get_all_venue_names():
    venues = get_field(venues_file(), 'name')
    return sorted(venues)


def get_venue_select_list():
    venues = get_fields(venues_file(), ['id', 'name'])
    return sorted(venues, key=lambda tup: tup[1])


def get_all_venues():
    venues = get_fields(venues_file(), [])
    return sorted(venues, key=lambda item: (item['name']))


def get_venue(venue_id):
    data = get_record(venues_file(), 'id', venue_id)
    data['address'] = decode_address(data['address'])
    data['directions'] = decode_directions(data['directions'])
    return data


def get_venue_by_name(name):
    res = get_record(venues_file(), 'name', name)
    res['address'] = decode_address(res['address'])
    res['directions'] = decode_directions(res['directions'])
    return res


def save_venue(venue_id, data):
    data['id'] = str(venue_id)
    data['name'] = data['name']
    data['url'] = data['url']
    data['phone'] = data['phone']
    data['address'] = encode_address(data['address'])
    data['directions'] = encode_directions(data['directions'])
    update_record(venues_file(), 'id', data)


def get_new_venue_id():
    ids = [int(m) for m in get_field(venues_file(), 'id')]
    return max(ids) + 1
# endregion


# region events

def create_events_file(year):
    directory = os.path.join(data_location, year)
    filename = events_file(year)
    fields = events_file_fields()
    return create_wags_data_file(directory, filename, fields)


def get_all_event_types():
    return [(e.name, e.name) for e in EventType]


def get_event_list(year):
    events = []
    for event_id in get_field(events_file(year), 'num'):
        event = get_event(year, event_id)
        if event:
            events.append(
                {
                    'num': event['num'],
                    'date': event['date'],
                    'event': event['event'],
                    'venue': event['course'] if is_tour_event(event) else event['venue'],
                    'type': event['event_type'],
                    'start_booking': event['start_booking'],
                    'end_booking': event['end_booking'],
                    'venue_url': event['url']
                }
            )
    return sorted(events, key=lambda item: (item['date'], to_float(item['num'])))


def get_event(year, event_id):
    year = coerce(year, int)
    event_id = coerce(event_id, str)
    data = get_record(events_file(year), 'num', event_id)
    if data['date']:
        data['date'] = decode_date(data['date'], year)
        data['end_booking'] = decode_date(data.get('deadline', None), year)
        data['start_booking'] = coerce_date(data.get('booking_start', None), year, data['date'])
        data['member_price'] = decode_price(data['member_price'])
        data['guest_price'] = decode_price(data['guest_price'])
        if (not data.get('type', None)) and 'tour' in data.get('event').lower():
            data['event_type'] = EventType.wags_tour
        else:
            data['event_type'] = decode_event_type(data.get('type', None))
        data['max'] = data.get('max', None)
        data['course'] = data.get('course', None)
        data['schedule'] = decode_schedule(data.get('schedule', None))
        data['note'] = dequote(data['note'])
        venue = get_venue_by_name(data.get('venue', None))
        data['address'] = venue['address']
        data['post_code'] = venue['post_code']
        data['phone'] = venue['phone']
        data['url'] = venue['url']
        data['directions'] = venue['directions']
        data['event'] = de_the(data['event'])
    else:
        data = None
    return data


def get_event_scores(year, event_id):
    date = event_date(year, event_id)
    course_id = str(event_course_id(year, event_id))
    if course_id in ['None', '0']:
        header, data = get_records(scores_file(), ['date'], [date])
    else:
        header, data = get_records(scores_file(), ['date', 'course'], [date, course_id])
    inx = lookup(header, ['player', 'position', 'points', 'strokes', 'handicap', 'status'])
    res = [itemgetter(*inx)(r) for r in data]
    return res


def get_event_cards(year, event_id):
    date = event_date(year, event_id)
    course_id = str(event_course_id(year, event_id))
    if course_id == '0':
        header, data = get_records(shots_file(), ['date'], [date])
    else:
        header, data = get_records(shots_file(), ['date', 'course'], [date, course_id])
    inx = lookup(header, ['player'] + [str(x) for x in range(1, 19)])
    return {r[inx[0]]: itemgetter(*inx[1:19])(r) for r in data}


def save_event_scores(year, event_id, header, data):
    date = event_date(year, event_id)
    course_id = str(event_course_id(year, event_id))
    update_records(scores_file(), ['date', 'course', 'player'], [date, course_id], header, data)


def update_event_scores(year, event_id, player_id, keys, values):
    date = event_date(year, event_id)
    course_id = str(event_course_id(year, event_id))
    update_records(scores_file(), ['date', 'course', 'player'], [date, course_id, player_id], keys, [values])


def get_event_card(year, event_id, player_id):
    player_id = coerce(player_id, str)
    date = event_date(year, event_id)
    return get_record(shots_file(), ['date', 'player'], [date, player_id])


def save_event_card(year, event_id, player_id, fields, shots):
    course_id = coerce(event_course_id(year, event_id), str)
    player_id = coerce(player_id, str)
    date = event_date(year, event_id)
    new = dict(zip(['date', 'course', 'player'] + fields, [date, course_id, player_id] + shots))
    update_record(shots_file(), ['date', 'course', 'player'], new)


def save_event(year, event_id, data):
    data['num'] = str(event_id)
    data['date'] = encode_date(data['date'])
    data['deadline'] = encode_date(data['end_booking'])
    data['member_price'] = encode_price(data['member_price'])
    data['guest_price'] = encode_price(data['guest_price'])
    data['booking_start'] = encode_date(data['start_booking'])
    data['type'] = encode_event_type(data['event_type'])
    data['schedule'] = encode_schedule(data['schedule'])
    insert_venue_info(data)
    update_record(events_file(year), 'num', data)


def insert_venue_info(event):
    venue = get_venue_by_name(event['venue'])
    event['address'] = dequote(encode_address(venue['address']))
    event['post_code'] = venue['post_code']
    event['phone'] = venue['phone']
    event['url'] = venue['url']
    event['directions'] = dequote(encode_directions(venue['directions']))


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


def get_new_event_id(year):
    ids = [float(m) for m in get_field(events_file(year), 'num')]
    return math.floor(1 + max(ids + [0]))


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
                if guest_handicap == '':
                    guest_handicap = '28'
                res.append([guest_name, guest_handicap])
                count += 1
    return {v[0]: v[1] for v in res}


def get_results(year, event_id):
    editable = is_event_editable(year)
    date = event_date(year, event_id)
    all_hcaps = dict(get_handicaps(date))
    all_scores = {v[0]: v[1:] for v in get_event_scores(year, event_id)}  # player: position, points, strokes, handicap, status
    all_players = get_all_player_names()
    booked = get_booked_players(year, event_id)  # player: handicap
    event_players = list(set(get_player_names(list(all_scores.keys()))) | set(booked.keys()))
    results = []
    for player in sort_name_list(event_players):
        player_id = str(lookup(all_players, player) + 1)
        guest = player in booked and to_float(booked[player]) > 0
        if player_id not in all_scores:
            if not editable:
                continue
            if guest:
                hcap = booked[player]
            else:
                hcap = all_hcaps[player_id]
            all_scores[player_id] = [0, '0', 0, hcap]
        det = all_scores[player_id]
        x = {
                'id': player_id,
                'name': player,
                'handicap': det[3],
                'strokes': int(det[2]),
                'points': int(det[1]),
                'position': int(det[0]),
                'guest': 'guest' if guest else ''
            }
        results.append(x)
    return sorted(results, key=lambda k: k['position'] if k['position'] > 0 else 99)


def get_event_by_year_and_name(year, event_name):
    event = get_record(events_file(year), 'course', event_name)
    return event


def get_results_by_year_and_name(year, event_name):
    event = get_event_by_year_and_name(year, event_name)
    return get_results(year, event['num'])


def event_course_id(year, event_id):
    event = get_event(year, event_id)
    course_id = lookup_course(event['venue'])
    return course_id


def event_date(year, event_id):
    event = get_event(year, event_id)
    date = fmt_date(event['date'])
    return date


def event_type(year, event_id):
    event = get_event(year, event_id)
    type = event['event_type']
    return type


def is_latest_event(event_id):
    today = datetime.date.today()
    year = today.year
    events = get_event_list(year)
    nums = [e['num'] for e in events if e['date'] <= today]
    if len(nums) > 0:
        return nums[-1] == event_id
    return False


def is_event_result_editable(year, event_id):
    event = get_event(year, event_id)
    override = config.get('override')
    return override or (datetime.date.today() > event['date'] and is_last_event(year, event_id))


def is_last_event(year, event_id):
    last = [str(x) for x in get_last_event()]
    override = config.get('override')
    return override or last == [str(year), str(event_id)]


def is_event_editable(year):
    override = config.get('override')
    return override or year >= datetime.date.today().year


def get_last_event(year=None):
    today = datetime.date.today()
    if not year:
        year = today.year
    events = get_event_list(year)
    nums = [e['num'] for e in events if e['type'] == EventType.wags_vl_event and e['date'] <= today]
    if len(nums) > 0:
        return year, nums[-1]
    return get_last_event(year-1)


# endregion


# region tours
def is_tour_event(event):
    return (not is_num(event['num'])) or float(event['num']) > math.floor(float(event['num']))


def get_tour_event_list(year, tour_event_id):
    tour_events = []
    tour_event_id = coerce(tour_event_id, int)
    for event_id in get_field(events_file(year), 'num'):
        id = to_float(event_id)
        if math.floor(id) == tour_event_id and id != tour_event_id:
            event = get_event(year, event_id)
            if event['event_type'] == EventType.wags_vl_event:
                tour_events.append(
                    {
                        'num': event['num'],
                        'date': event['date'],
                        'course': event['course'],
                        'venue': event['venue']
                    }
                )
    if len(tour_events) > 0:
        return tour_events
    return get_tour_event_list_from_scores(year, tour_event_id)


def get_tour_event_list_from_scores(year, tour_event_id):
    tour_events = []
    tour_event = get_record(events_file(year), 'num', str(tour_event_id))
    date_range = decode_date_range(tour_event['date'], year)

    def lu_fn(rec, key, date_range):
        date = parse_date(rec[key])
        res = date_range[0] <= date <= date_range[1]
        return res
    scores = Table(*get_records(scores_file(), 'date', date_range, lu_fn))
    date_course = sorted([s[0] for s in scores.groupby(['date', 'course'])])
    id = tour_event_id
    for event in date_course:
        id += 0.1
        tour_events.append(
            {
                'num': str(round(id, 1)),
                'date': parse_date(event[0]),
                'course': get_course(event[1])['name'],
                'venue': get_course(event[1])['name']
            }
        )
    return tour_events


def get_tour_event_ids(year, tour_event_id):
    event_ids = []
    tour_event_id = coerce(tour_event_id, int)
    for event_id in get_field(events_file(year), 'num'):
        id = to_float(event_id)
        if math.floor(id) == tour_event_id and id != tour_event_id:
            event_ids.append(id)
    return event_ids


def get_tour_events(year, tour_event_id, max):
    events = get_tour_event_list(year, tour_event_id)
    count = len(events)
    while count < max:
        e = {
            'num': None,
            'date': None,
            'course': None,
            'venue': None
            }
        events.append(e)
        count += 1
    return events


def get_tour_scores(year, event_id):
    events = get_tour_event_list(year, event_id)
    dates = []
    course_ids = []
    for event in events:
        dates.append(event['date'].strftime('%Y/%m/%d'))
        course_ids.append(str(lookup_course(event['course'])))

    def lu_fn(rec, keys, values):
        dates, courses = values
        res = rec[keys[0]] in dates and rec[keys[1]] in courses
        return res

    res = get_records(scores_file(), ['date', 'course'], [dates, course_ids], lu_fn)
    return res

# endregion


# region courses
def get_all_course_names():
    courses = get_field(courses_file(), 'name')
    return sorted(courses)


def get_course_names(course_ids):
    head, recs = get_records(courses_file(), 'id', course_ids)
    recs = {r[lookup(head, 'id')]: r[lookup(head, 'name')] for r in recs}
    return [recs[p] for p in course_ids]


def get_course(course_id):
    course_id = coerce(course_id, str)
    data = get_record(courses_file(), 'id', course_id)
    return data


def get_courses_for_venue(venue_id):
    return get_records(courses_file(), 'venue_id', venue_id)


def lookup_course(course):
    rec = get_record(venues_file(), 'name', course)
    return rec['id'] if len(rec) > 0 else '0'


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


def get_new_course_id():
    ids = [int(m) for m in get_field(courses_file(), 'id')]
    return 1 + max(ids)


def save_course(course_id, data):
    data['id'] = str(course_id)
    data['venue_id'] = data['venue_id']
    data['name'] = data['name']
    update_record(courses_file(), 'id', data)


def save_course_card(course_id, year, fields, data):
    course_id = coerce(course_id, str)
    new = dict(zip(['course', 'year'] + fields, [course_id, year] + data))
    update_record(course_data_file(), ['course', 'year'], new)

# endregion


# region players

def get_all_player_names():
    data = get_field(players_file(), 'name')
    return data


def get_player_name(player_id):
    rec = get_record(players_file(), 'id', player_id)
    return rec['name']


def get_player_id(player_name):
    rec = get_record(players_file(), 'name', player_name)
    return rec['id']


def get_player_names(player_ids):
    head, recs = get_records(players_file(), 'id', player_ids)
    recs = {r[0]: r[1] for r in recs}
    return [recs[p] for p in player_ids]


def get_players(as_of, status=None):
    header, recs = get_handicap_records(as_of, status)
    inx = [1]
    pi = [int(itemgetter(*inx)(r)) - 1 for r in recs]
    players = get_all_player_names()
    current = itemgetter(*pi)(players)
    return sort_name_list(current)


def get_handicaps(as_of, status=None):
    header, recs = get_handicap_records(as_of, status)
    inx = lookup(header, ['player', 'handicap'])
    return [itemgetter(*inx)(r) for r in recs]


def get_player_handicap(player_id, as_of):
    player_id = coerce(player_id, str)
    as_of = coerce_fmt_date(as_of)
    header, recs = get_records(handicaps_file(), 'player', player_id)
    recs = [x for x in recs if x[0] <= as_of]
    recs.sort(key=lambda tup: (tup[1], tup[0]), reverse=True)
    return float(dict(zip(header, recs[0]))['handicap'])


def get_handicap_records(as_of, status=None):
    as_of = coerce_fmt_date(as_of)
    if status is not None:
        status = force_list(status)

    def lu_fn(rec, keys, values):
        date, status = values
        res = rec[keys[0]] <= date
        if status is not None:
            status = [str(s) for s in status]
            res = res and rec[keys[1]] in status
        return res

    header, recs = get_records(handicaps_file(), ['date', 'status'], [as_of, status], lu_fn)
    recs.sort(key=lambda tup: (tup[1], tup[0]), reverse=True)  # order by date within player
    get_item = itemgetter(lookup(header, 'player'))
    res = [list(value)[0] for key, value in groupby(recs, get_item)]  # get latest for each player
    return header, res


def get_handicap_history(player_id, as_of):
    player_id = coerce(player_id, str)
    as_of = coerce_fmt_date(as_of)
    header, recs = get_records(handicaps_file(), 'player', player_id)
    recs = [x for x in recs if x[0] <= as_of]
    recs.sort(key=lambda tup: (tup[1], tup[0]), reverse=True)
    inx = lookup(header, ['date', 'handicap', 'status'])
    res = [itemgetter(*inx)(r) for r in recs]
    return res


def get_player_scores(player_id, year=None):
    def lu_fn(rec, keys, values):
        player_id, year = values
        res = player_id == rec[keys[0]]
        if year is not None:
            res = res and year == parse_date(rec[keys[1]]).year
        return res

    scores = get_records(scores_file(), ['player', 'date'], [player_id, coerce(year, int)], lu_fn)
    return scores


def add_player(name, hcap, status, date):
    all_players = get_all_player_names()
    if lookup(all_players, name) != -1:
        raise Exception("Player {} already exists, can't add.".format(name))
    id = str(len(all_players) + 1)
    update_record(players_file(), 'id', [id, name])
    date = coerce_fmt_date(date)
    update_record(handicaps_file(), ['date', 'player'], [date, id, hcap, status])

    return id


def save_handicaps(date, header, data):
    update_records(handicaps_file(), ['date', 'player'], [date], header, data)

# endregion


def get_scores(year, status=None):
    if status is not None:
        status = force_list(status)

    def lu_fn(rec, keys, values):
        year, status = values
        res = year == parse_date(rec[keys[0]]).year
        if status is not None:
            status = [str(s) for s in status]
            res = res and rec[keys[1]] in status
        return res
    scores = get_records(scores_file(), ['date', 'status'], [coerce(year, int), status], lu_fn)
    return scores


# region admin
def get_admin_user(key, value):
    return get_record(admin_users_file(), key, str(value))


def add_admin_user(user):
    all = get_field(admin_users_file(), 'id')
    user.set_id(len(all) + 1)
    update_record(admin_users_file(), 'id', user.record())


def get_current_members():
    header, data = get_records(members_file(), ['status'], [str(PlayerStatus.member)])
    i = lookup(header, ['salutation', 'surname'])
    member_names = sort_name_list([' '.join(itemgetter(*i)(m)) for m in data])
    all_players = get_all_player_names()
    pid = lookup(all_players, member_names, index_origin=1)
    return OrderedDict(zip(pid, member_names))


def get_members(as_of):
    def lu_fn(rec, key, value):
        date = rec[key]
        return parse_date(date) > value
    header, data = get_records(members_file(), 'resigned', parse_date(as_of), lu_fn)
    i = lookup(header, ['salutation', 'surname'])
    member_names = sort_name_list([' '.join(itemgetter(*i)(m)) for m in data])
    all_players = get_all_player_names()
    pid = lookup(all_players, member_names, index_origin=1)
    return OrderedDict(zip(pid, member_names))


def get_member(key, value):
    return get_record(members_file(), key, value)
# endregion


def get_all_years():
    current_year = datetime.datetime.now().year
    inc = 1 if datetime.datetime.now().month > 10 else 0
    years = [i for i in range(current_year + inc, 1992, -1)]
    return years


def get_all_trophy_names():
    trophies = get_field(trophies_file(), 'name')
    return sorted(trophies)


def get_trophy_url(event):
    trophy = event.lower().replace(" ", "_").replace("-", "")
    url = url_for_old_site("history/trophies/")
    return url + trophy + '.htm'


def get_venue_url(year, url):
    if url:
        if url.startswith("/"):
            url = url_for_old_site('{}/{}'.format(year, url[1:]))
        else:
            url = '//' + url
    else:
        url = '/not_found'
    return url


def create_bookings_file(year, event_id):
    directory = os.path.join(data_location, str(year))
    filename = bookings_file(year, event_id)
    fields = bookings_file_fields()
    return create_wags_data_file(directory, filename, fields, access_all=True)


def create_wags_data_file(directory, filename, fields, access_all=False):
    result = True
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.exists(filename):
            create_data_file(filename, fields, access_all)
    except:
        e = sys.exc_info()[0]
        result = False
    return result


def get_all_news():
    res = get_news_file(news_file())
    return res

import datetime
import os

from back_end.data_utilities import lookup, sort_name_list, fmt_num, mean, first_or_default
from back_end.table import Table
from globals.enumerations import MemberStatus, PlayerStatus, EventType
from models.wags_db_new import Event, Score, Course, CourseData, Trophy, Player, Venue, Handicap, \
    Member  # , Member, EnumType
from globals.db_setup import db_session
from sqlalchemy import text

from globals import config
from back_end.file_access import get_field, get_record, update_record, get_records

data_location = config.get('locations')['data']
admin_users = r'admin_users.txt'
bookings_data = r'{}/event{}.csv'


def admin_users_file():
    return os.path.join(data_location, admin_users)


def bookings_file(year, event_id):
    return os.path.join(data_location, bookings_data.format(year, event_id))


def bookings_file_fields():
    return ['date', 'name', 'playing', 'number', 'cost', 'paid', 'guest1', 'guest1_hcap', 'guest2', 'guest2_hcap',
            'guest3', 'guest3_hcap', 'comment']


def gen_to_list(gen):
    # force evaluation of a generator
    return [x for x in gen]


# region venues
def get_all_venue_names():
    return [v.name for v in db_session.query(Venue).order_by(Venue.name)]


def get_venue_select_list():
    pass
    # venues = get_fields(venues_file(), ['id', 'name'])
    # return sorted(venues, key=lambda tup: tup[1])


def get_all_venues():
    pass
    # venues = get_fields(venues_file(), [])
    # return sorted(venues, key=lambda item: (item['name']))


def get_venue(venue_id):
    pass
    # data = get_record(venues_file(), 'id', venue_id)
    # data['address'] = decode_address(data['address'])
    # data['directions'] = decode_directions(data['directions'])
    # return data


def get_venue_by_name(name):
    pass
    # res = get_record(venues_file(), 'name', name)
    # res['address'] = decode_address(res['address'])
    # res['directions'] = decode_directions(res['directions'])
    # return res


def save_venue(venue_id, data):
    pass
    # data['id'] = str(venue_id)
    # data['name'] = data['name']
    # data['url'] = data['url']
    # data['phone'] = data['phone']
    # data['address'] = encode_address(data['address'])
    # data['directions'] = encode_directions(data['directions'])
    # update_record(venues_file(), 'id', data)


def get_new_venue_id():
    pass
    # ids = [int(m) for m in get_field(venues_file(), 'id')]
    # return max(ids) + 1


def get_venue_url(year, url):
    if url:
        if url.startswith("/"):
            url = config.url_for_old_site('{}/{}'.format(year, url[1:]))
        else:
            url = '//' + url
    else:
        url = '/not_found'
    return url


# endregion


# region events

def create_events_file(year):
    pass
    # directory = os.path.join(data_location, year)
    # filename = events_file(year)
    # fields = events_file_fields()
    # return create_wags_data_file(directory, filename, fields)


def get_event(event_id):
    return db_session.query(Event).filter_by(id=event_id).first() or Event(id=0, date=datetime.datetime.now().date())


def get_events_for_year(year):
    stmt = text("select id from events where strftime('%Y', date)=:year order by date, type desc").params(
        year=str(year))
    return db_session.query(Event).from_statement(stmt)


def get_event_list(year):
    events = []
    for event in get_events_for_year(year):
        if event.venue.contact:
            url = event.venue.contact.url
        else:
            url = None
        if event.trophy:
            trophy = event.trophy.name
            trophy_url = event.trophy.url()
        else:
            trophy = ''
        events.append(
            {
                'num': event.id,
                'date': event.date,
                'event': trophy,
                'trophy_url': trophy_url,
                'venue': event.venue.name,
                'type': event.type,
                'tour_id': event.tour_event_id,
                'start_booking': event.booking_start,
                'end_booking': event.booking_end,
                'venue_url': url
            }
        )
    return events


def get_event_select_list():
    pass
    # events = set(get_fields(scores_file(), ['date', 'course']))
    # events = sorted(events, key=lambda dc: dc[0], reverse=True)
    # date, course_ids = zip(*events)
    # course = get_course_names(list(course_ids))
    # return [dc[0] + '-' + dc[1] for dc in zip(date, course)]


def get_event_scores(event_id):
    event = get_event(event_id)
    head = ['player_id', 'position', 'points', 'shots', 'handicap', 'status', 'card']
    data = []
    for score in event.scores:
        player_state = score.player.state_as_of(event.date)
        row = [score.player_id,
               score.position,
               score.points,
               score.shots,
               player_state.handicap,
               player_state.status,
               score.card]
        data.append(row)
    return Table(head, data)


def get_event_cards(event_id):
    scores = db_session.query(Score).filter(Score.event_id == event_id)
    return {s.player_id: s.card for s in scores}


def get_cards(course_id, date):
    pass
    # if course_id == '0':
    #     header, data = get_records(shots_file(), ['date'], [date])
    # else:
    #     header, data = get_records(shots_file(), ['date', 'course'], [date, course_id])
    # inx = lookup(header, ['player'] + [str(x) for x in range(1, 19)])
    # return {r[inx[0]]: itemgetter(*inx[1:19])(r) for r in data}


def save_event_result(event_id, result):
    event = get_event(event_id)
    scores = []
    delete = [True] * len(event.scores)
    for row in result.data:
        new = dict(zip(result.head, row))
        score = first_or_default([s for s in event.scores if s.player_id == int(new['player_id'])], None)
        if score:
            score.position = new['position']
            score.shots = new['shots']
            score.points = new['points']
            delete[lookup(event.scores, score)] = False
        else:
            score = Score(event_id=event_id,
                          player_id=new['player_id'],
                          position=new['position'],
                          shots=new['shots'],
                          points=new['points'],
                          card=None)
        scores.append(score)
    for score in event.scores:
        if delete[lookup(event.scores, score)]:
            db_session.delete(score)
    if len(result.data) > 0:
        event.winner_id = result.get_columns('player_id')[0]
        event.average_score = "{0:.1f}".format(mean(result.get_columns('points')))
    else:
        event.winner_id = event.average_score = None
    event.scores = scores
    db_session.commit()


def get_event_card(event_id, player_id):
    score = db_session.query(Score).filter(Score.event_id == event_id, Score.player_id == player_id).first()
    if score:
        if score.card:
            return score.card
    return [99] * 18


def save_event_score(event_id, player_id, position, card, shots, points):
    event = get_event(event_id)
    score = first_or_default([s for s in event.scores if s.player_id == player_id], None)
    if score:
        score.position = position
        score.card = card
        score.shots = shots
        score.points = points
    else:
        score = Score(event_id=event_id,
                      player_id=player_id,
                      position=position,
                      shots=shots,
                      points=points,
                      card=card)
        event.scores.append(score)
    db_session.commit()


def save_event(event_id, data):
    pass
    # data['num'] = str(event_id)
    # data['date'] = encode_date(data['date'])
    # data['deadline'] = encode_date(data['end_booking'])
    # data['member_price'] = encode_price(data['member_price'])
    # data['guest_price'] = encode_price(data['guest_price'])
    # data['booking_start'] = encode_date(data['start_booking'])
    # data['type'] = encode_event_type(data['event_type'])
    # data['schedule'] = encode_schedule(data['schedule'])
    # data['note'] = encode_newlines(data['note'])
    # insert_venue_info(data)
    # update_record(events_file(year), 'num', data)


def insert_venue_info(event):
    pass
    # venue = get_venue_by_name(event['venue'])
    # event['address'] = encode_address(venue['address'])
    # event['post_code'] = venue['post_code']
    # event['phone'] = venue['phone']
    # event['url'] = venue['url']
    # event['directions'] = encode_directions(venue['directions'])


def decode_schedule(sched):
    pass
    # # schedule is comma delimited set of items,
    # # each item in form: hh.mm text  e.g. 10.30 Tee-off 18 holes
    # if sched:
    #     ss = [(t.strip()).split(' ', 1) for t in sched.split(',')]
    # else:
    #     ss = []
    # while len(ss) < 6:
    #     ss.append([None, None])
    # return [{'time': decode_time(s[0]), 'text': s[1]} for s in ss]


def encode_schedule(sched):
    pass
    # # return schedule to external form (see decode_schedule)
    # ss = [s for s in sched if (not empty_schedule_item(s))]
    # ss = sorted(ss, key=lambda k: k['time'])
    # ss = [(s['time'].strftime('%H.%M')) + ' ' + s['text'].replace(',', '').replace(':', '-') for s in ss]
    # ss = ','.join(ss)
    # return ss


def empty_schedule_item(item):
    pass
    # return (not item['text']) and item['time'].hour == 0 and item['time'].minute == 0


def get_new_event_id(year):
    pass
    # ids = [float(m) for m in get_field(events_file(year), 'num')]
    # return math.floor(1 + max(ids + [0]))


def get_booked_players(event):
    year = event.date.year
    event_dates = [event.date for event in get_events_for_year(year)]
    event_num = lookup(event_dates, event.date, index_origin=1)
    file = bookings_file(year, event_num)
    if not os.path.isfile(file):
        file = bookings_file(year, 0)
    header, bookings = get_records(file, 'playing', '1')
    res = {}
    all_players = get_players_as_of(event.date)
    all_player_names = list(all_players.keys())
    for b in bookings:
        booking = dict(zip(header, b))
        number = int(booking['number'])
        if number > 0:
            name = normalise_name(all_player_names, booking['name'])
            res[name] = all_players[name]
            count = 1
            while count < number:
                guest_name = normalise_name(all_player_names, booking['guest' + str(count)])
                guest_handicap = booking['guest' + str(count) + '_hcap']
                if guest_handicap == '':
                    guest_handicap = '28'
                if guest_name in all_players:
                    res[guest_name] = all_players[guest_name]
                else:
                    state = Handicap(player_id=0, status=PlayerStatus.guest, handicap=int(guest_handicap),
                                     date=datetime.datetime.today)
                    res[guest_name] = state
                count += 1
    return res


def normalise_name(all_names, name):
    i = lookup(all_names, name, case_sensitive=False)
    if i == -1:
        return name
    else:
        return all_names[i]


def get_results(event):
    '''Returns all results for an event. Adds any players that were booked but without any recorded scores yet.'''
    players = []
    results = []
    for score in [s for s in event.scores]:
        player = score.player
        state = player.state_as_of(event.date)
        players.append(player.full_name())
        x = {
            'player': player.full_name(),
            'handicap': state.handicap,
            'points': score.points or 0,
            'strokes': score.shots,
            'position': score.position or 0,
            'player_id': player.id,
            'status': state.status,
            'card:': score.card
        }
        results.append(x)
    booked = get_booked_players(event)
    for missing in list(set(booked.keys()).difference(set(players))):
        state = booked[missing]
        x = {
            'player': missing,
            'handicap': state.handicap,
            'points': 0,
            'strokes': 0,
            'position': 0,
            'player_id': state.player_id,
            'status': state.status,
            'card': None
        }
        results.append(x)

    results.sort(key=lambda k: k['player'])
    results.sort(key=lambda k: k['position'] if k['points'] > 0 else 99)
    i = 0
    for res in results:
        i += 1
        res['position'] = i
    return results


def get_event_by_year_and_name(year, event_name):
    pass
    # event = {'num': None}
    # if os.path.exists(events_file(year)):
    #     event = get_record(events_file(year), 'course', event_name)
    #     if not event['num']:
    #         event = get_record(events_file(year), 'venue', event_name)
    # return event


def get_results_by_year_and_name(year, event_name):
    pass
    # event = get_event_by_year_and_name(year, event_name)
    # return get_results_for_edit(year, event['num'])


def event_course_id(year, event_id):
    pass
    # event = get_event(year, event_id)
    # course_id = lookup_course(event['course'])
    # return course_id


def event_venue_id(year, event_id):
    pass
    # event = get_event(year, event_id)
    # event_id = get_venue_by_name(event['venue'])['id']
    # return event_id


def event_trophy_id(year, event_id):
    pass
    # event = get_event(year, event_id)
    # trophy_id = get_trophy_by_name(event['event'])['id']
    # return trophy_id


def event_date(year, event_id):
    pass
    # event = get_event(year, event_id)
    # date = fmt_date(event['date'])
    # return date


def event_title(year, event_id):
    pass
    # event = get_event(year, event_id)
    # venue = event['venue']
    # date = fmt_date(event['date'])
    # return venue + ' ' + date


def event_type(year, event_id):
    pass
    # event = get_event(year, event_id)
    # type = event['event_type']
    # return type


def is_latest_event(event_id):
    pass
    # today = datetime.date.today()
    # year = today.year
    # events = get_event_list(year)
    # nums = [e['num'] for e in events if e['date'] <= today]
    # if len(nums) > 0:
    #     return nums[-1] == event_id
    # return False


def is_event_result_editable(event):
    override = config.get('override')
    return override or (datetime.date.today() > event.date)  # and is_last_event(event))


def is_last_event(event):
    last = get_last_event(event.date.year)
    override = config.get('override')
    return override or event.id == last.id


def is_event_editable(year):
    override = config.get('override')
    return override or year >= datetime.date.today().year


def get_last_event(year):
    past = [e for e in get_events_for_year(year) if e.type == EventType.wags_vl_event and e.date <= datetime.date.today()]
    if len(past) > 0:
        return past[-1]
    return get_last_event(year - 1)


def get_next_event(year=None):
    pass
    # today = datetime.date.today()
    # if not year:
    #     year = today.year
    # events = get_event_list(year)
    # nums = [e['num'] for e in events if e['type'] == EventType.wags_vl_event and e['date'] > today]
    # if len(nums) > 0:
    #     return year, nums[0]
    # return get_next_event(year + 1)


def get_events_in(date_range):
    pass
    # def lu_fn(rec, key, date_range):
    #     date = parse_date(rec[key])
    #     res = date_range[0] <= date <= date_range[1]
    #     return res
    #
    # scores = Table(*get_records(scores_file(), 'date', date_range, lu_fn))
    # scores.sort('date')
    # events = [e[0] for e in scores.groupby(['date', 'course'])]
    # return events


# endregion


# region tours
def is_tour_event(event):
    pass
    # return (not is_num(event['num'])) or float(event['num']) > math.floor(float(event['num']))


def get_tour_event_list(year, tour_event_id):
    pass
    # tour_events = []
    # tour_event_id = coerce(tour_event_id, int)
    # for event_id in get_field(events_file(year), 'num'):
    #     id = to_float(event_id)
    #     if math.floor(id) == tour_event_id and id != tour_event_id:
    #         event = get_event(year, event_id)
    #         if event['event_type'] == EventType.wags_vl_event:
    #             tour_events.append(
    #                 {
    #                     'num': event['num'],
    #                     'date': event['date'],
    #                     'course': event['course'],
    #                     'venue': event['venue']
    #                 }
    #             )
    # if len(tour_events) > 0:
    #     return tour_events
    # return get_tour_event_list_from_scores(year, tour_event_id)


def get_tour_event_list_from_scores(year, tour_event_id):
    pass
    # tour_events = []
    # tour_event = get_record(events_file(year), 'num', str(tour_event_id))
    # date_range = decode_date_range(tour_event['date'], year)
    #
    # def lu_fn(rec, key, date_range):
    #     date = parse_date(rec[key])
    #     res = date_range[0] <= date <= date_range[1]
    #     return res
    #
    # scores = Table(*get_records(scores_file(), 'date', date_range, lu_fn))
    # date_course = sorted([s[0] for s in scores.groupby(['date', 'course'])])
    # id = tour_event_id
    # for event in date_course:
    #     id += 0.1
    #     tour_events.append(
    #         {
    #             'num': str(round(id, 1)),
    #             'date': parse_date(event[0]),
    #             'course': get_course(event[1])['name'],
    #             'venue': get_course(event[1])['name']
    #         }
    #     )
    # return tour_events


def get_tour_event_ids(year, tour_event_id):
    pass
    # event_ids = []
    # tour_event_id = coerce(tour_event_id, int)
    # for event_id in get_field(events_file(year), 'num'):
    #     id = to_float(event_id)
    #     if math.floor(id) == tour_event_id and id != tour_event_id:
    #         event_ids.append(id)
    # return event_ids


def get_tour_events(year, tour_event_id, max):
    pass
    # events = get_tour_event_list(year, tour_event_id)
    # count = len(events)
    # while count < max:
    #     e = {
    #         'num': None,
    #         'date': None,
    #         'course': None,
    #         'venue': None
    #     }
    #     events.append(e)
    #     count += 1
    # return events


def get_tour_scores(event_ids):
    ids = '(' + (','.join([str(id) for id in event_ids])) + ')'
    s = text("select * from scores where event_id in {} order by player_id, event_id".format(ids))
    scores = []
    for score in db_session.query(Score).from_statement(s):
        scores.append([score.event_id, score.player_id, score.points])
    head = ['event', 'player', 'points']
    return head, scores


# endregion


# region courses
def get_all_course_names():
    return [c.name for c in db_session.query(Course).order_by(Course.name)]


def get_course_names(course_ids):
    pass
    # head, recs = get_records(courses_file(), 'id', course_ids)
    # recs = {r[lookup(head, 'id')]: r[lookup(head, 'name')] for r in recs}
    # return [recs[p] for p in course_ids]


def get_course(course_id):
    pass
    # course_id = coerce(course_id, str)
    # data = get_record(courses_file(), 'id', course_id)
    # return data


def get_courses_for_venue(venue_id):
    pass
    # return get_records(courses_file(), 'venue_id', venue_id)


def get_course_for_date(date):
    pass
    # scores = get_all_scores(key='date', values=[date])
    # if len(scores[1]) > 1:
    #     course_id = scores[1][1][scores[0].index('course')]
    #     return get_record(courses_file(), 'id', course_id)
    # else:
    #     return None


def lookup_course(course):
    pass
    # rec = get_record(venues_file(), 'name', course)
    # return rec['id'] if len(rec) > 0 else '0'


def get_course_data(course_id, year):
    stmt = text("select * from course_data where course_id=:course_id and year>=:year order by year")
    stmt = stmt.columns(CourseData.course_id, CourseData.year, CourseData.sss, CourseData.si, CourseData.par)
    return db_session.query(CourseData).from_statement(stmt).params(course_id=course_id, year=year).first()


def get_new_course_id():
    pass
    # ids = [int(m) for m in get_field(courses_file(), 'id')]
    # return 1 + max(ids)


def save_course(course_id, data):
    pass
    # data['id'] = str(course_id)
    # data['venue_id'] = data['venue_id']
    # data['name'] = data['name']
    # update_record(courses_file(), 'id', data)


def save_course_card(course_id, year, fields, data):
    pass
    # course_id = coerce(course_id, str)
    # new = dict(zip(['course', 'year'] + fields, [course_id, year] + data))
    # update_record(course_data_file(), ['course', 'year'], new)


# endregion


# region players

def get_players_as_of(date):
    res = {}
    for p in db_session.query(Player).order_by(Player.last_name, Player.first_name):
        state = p.state_as_of(date)
        res[p.full_name()] = state
    return res


def get_player_names(player_ids):
    ids = '(' + (','.join([str(id) for id in player_ids])) + ')'
    s = text("select * from players where id in {}".format(ids))
    players = {}
    for player in db_session.query(Player).from_statement(s):
        players[player.id] = player.full_name()
    return players


def get_player(player_id):
    return db_session.query(Player).filter(Player.id == player_id).first()


def get_player_id(player_name):
    pass
    # rec = get_record(players_file(), 'name', player_name)
    # return rec['id']


def get_players(as_of, status=None):
    pass
    # header, recs = get_handicap_records(course_data_as_of, status)
    # inx = [1]
    # pi = [int(itemgetter(*inx)(r)) - 1 for r in recs]
    # players = get_all_player_names()
    # current = itemgetter(*pi)(players)
    # return sort_name_list(current)


def get_player_select_list():
    pass
    # players = get_fields(players_file(), ['id', 'name'])
    # return sorted(players, key=lambda tup: tup[1])


def get_handicaps(as_of, status=None):
    pass
    # header, recs = get_handicap_records(course_data_as_of, status)
    # inx = lookup(header, ['player', 'handicap'])
    # return [itemgetter(*inx)(r) for r in recs]


def get_player_handicap(player_id, as_of):
    pass
    # player_id = coerce(player_id, str)
    # course_data_as_of = coerce_fmt_date(course_data_as_of)
    # header, recs = get_records(handicaps_file(), 'player', player_id)
    # recs = [x for x in recs if x[0] <= course_data_as_of]
    # recs.sort(key=lambda tup: (tup[1], tup[0]), reverse=True)
    # return float(dict(zip(header, recs[0]))['handicap'])


def get_handicap_records(as_of, status=None):
    pass
    # course_data_as_of = coerce_fmt_date(course_data_as_of)
    # if status is not None:
    #     status = force_list(status)
    #
    # def lu_fn(rec, keys, values):
    #     date, status = values
    #     res = rec[keys[0]] <= date
    #     if status is not None:
    #         status = [str(s) for s in status]
    #         res = res and rec[keys[1]] in status
    #     return res
    #
    # header, recs = get_records(handicaps_file(), ['date', 'status'], [course_data_as_of, status], lu_fn)
    # recs.sort(key=lambda tup: (tup[1], tup[0]), reverse=True)  # order by date within player
    # get_item = itemgetter(lookup(header, 'player'))
    # res = [list(value)[0] for key, value in groupby(recs, get_item)]  # get latest for each player
    # return header, res


def get_handicap_history(player_id, as_of):
    pass
    # player_id = coerce(player_id, str)
    # course_data_as_of = coerce_fmt_date(course_data_as_of)
    # header, recs = get_records(handicaps_file(), 'player', player_id)
    # recs = [x for x in recs if x[0] <= course_data_as_of]
    # recs.sort(key=lambda tup: (tup[1], tup[0]), reverse=True)
    # inx = lookup(header, ['date', 'handicap', 'status'])
    # res = [itemgetter(*inx)(r) for r in recs]
    # return res


def get_player_scores(player_id, year=None):
    pass
    # def lu_fn(rec, keys, values):
    #     player_id, year = values
    #     res = player_id == rec[keys[0]]
    #     if year is not None:
    #         res = res and year == parse_date(rec[keys[1]]).year
    #     return res
    #
    # scores = get_records(scores_file(), ['player', 'date'], [player_id, coerce(year, int)], lu_fn)
    # return scores


def add_player(name, hcap, status, date):
    first, last = name.split(' ')
    player = Player(first_name=first, last_name=last)
    player.handicaps.append(Handicap(date=date, handicap=hcap, status=status))
    db_session.add(player)
    db_session.commit()
    return player.id
    pass
    # all_players = get_all_player_names()
    # if lookup(all_players, name) != -1:
    #     raise Exception("Player {} already exists, can't add.".format(name))
    # id = str(len(all_players) + 1)
    # update_record(players_file(), 'id', [id, name])
    # date = coerce_fmt_date(date)
    # update_record(handicaps_file(), ['date', 'player'], [date, id, hcap, status])
    # return id


def update_player_handicap(player_id, hcap, status, date):
    pass
    # update_record(handicaps_file(), ['date', 'player'], [date, player_id, hcap, status])


def update_player_name(player_id, name):
    pass
    # update_record(players_file(), 'id', [player_id, name])


def save_handicaps(date, header, data):
    pass
    # update_records(handicaps_file(), ['date', 'player'], [date], header, data)


# endregion


# region admin
def get_admin_user(key, value):
    return get_record(admin_users_file(), key, str(value))


def add_admin_user(user):
    all = get_field(admin_users_file(), 'id')
    user.set_id(len(all) + 1)
    update_record(admin_users_file(), 'id', user.record())


# endregion


# region Members
def get_current_members():
    members = db_session.query(Member).filter_by(status=MemberStatus.full_member)
    players = [m.player for m in members]

    def sk(player):
        return player.last_name.lower() + player.first_name.lower()

    players.sort(key=sk)
    return players


def get_all_members():
    pass
    # header, data = get_all_records(members_file())
    # i = lookup(header, ['salutation', 'surname'])
    # member_names = sort_name_list([' '.join(itemgetter(*i)(m)) for m in data])
    # all_players = get_all_player_names()
    # pid = lookup(all_players, member_names, index_origin=1)
    # return OrderedDict(zip(pid, member_names))


def get_member_select_list():
    choices = [(p.member.id, p.full_name()) for p in get_current_members()]
    return choices


def get_new_member_id():
    pass
    # ids = get_field(members_file(), 'membcode')
    # ids.sort()
    # last = ids[-1]
    # next = 'WAG' + str(1 + int(last[-3:]))
    # return next


def save_member(data):
    pass
    # update_record(members_file(), 'membcode', data)


def get_members(as_of):
    pass
    # def lu_fn(rec, key, value):
    #     date = rec[key]
    #     return parse_date(date) > value
    #
    # header, data = get_records(members_file(), 'resigned', parse_date(course_data_as_of), lu_fn)
    # i = lookup(header, ['salutation', 'surname'])
    # member_names = sort_name_list([' '.join(itemgetter(*i)(m)) for m in data])
    # all_players = get_all_player_names()
    # pid = lookup(all_players, member_names, index_origin=1)
    # return OrderedDict(zip(pid, member_names))


def get_member(key, value):
    pass
    # return get_record(members_file(), key, value)


# endregion


# region Trophies
def get_all_trophy_names():
    return [t.name for t in db_session.query(Trophy).order_by(Trophy.name)]


def get_trophy(trophy_id):
    return db_session.query(Trophy).filter_by(id=trophy_id).first()


def get_trophy_by_name(name):
    pass
    # rec = get_record(trophies_file(), 'name', name)
    # return rec


def get_trophy_select_list():
    pass
    # trophies = get_fields(trophies_file(), ['id', 'name'])
    # return sorted(trophies, key=lambda tup: tup[1])


def get_trophy_history(trophy_id):
    pass
    # rec = get_records(trophy_history_file(), 'trophy', trophy_id)
    # return rec


def get_all_trophies():
    pass
    # rec = get_all_records(trophies_file())
    # return rec


def get_all_trophy_history():
    pass
    # rec = get_all_records(trophy_history_file())
    # return rec


def get_trophy_url(url):
    pass
    # trophy = get_trophy_by_name(event)
    # if trophy['id']:
    #     return config.url_for_user('trophy', trophy=trophy['id'])
    # trophy = event.lower().replace(" ", "_").replace("-", "")
    # url = config.url_for_old_site("history/trophies/")
    # return url + trophy + '.htm'


def update_trophy_history(year, event_id, result):
    pass
    # date = event_date(year, event_id)
    # venue_id = str(event_venue_id(year, event_id))
    # trophy_id = str(event_trophy_id(year, event_id))
    #
    # def sel_fn(values):
    #     return values['status'] == str(MemberStatus.full_member.value)
    # result = result.select_rows(sel_fn)
    # winner = result.get_columns('player')[0]
    # scores = result.get_columns('points')
    # average = "{0:.1f}".format(mean(scores))
    # rec = dict(zip(['trophy', 'date', 'venue', 'winner', 'score', 'average'],
    #                [trophy_id, date, venue_id, winner, scores[0], average]))
    # update_record(trophy_history_file(), ['trophy', 'date'], rec)


# endregion


# region Scores
def get_scores(year, status=None):
    pass
    # if status is not None:
    #     status = force_list(status)
    #
    # def lu_fn(rec, keys, values):
    #     year, status = values
    #     res = year == parse_date(rec[keys[0]]).year
    #     if status is not None:
    #         status = [str(s) for s in status]
    #         res = res and rec[keys[1]] in status
    #     return res
    #
    # scores = get_records(scores_file(), ['date', 'status'], [coerce(year, int), status], lu_fn)
    # return scores


def get_all_scores(key=None, values=None):
    pass
    # if key is None and values is None:
    #     return get_all_records(scores_file())
    # else:
    #     values = [str(v) for v in force_list(values)]
    #     return get_records(scores_file(), key, values)


# endregion


def get_all_years():
    current_year = datetime.datetime.now().year
    inc = 1 if datetime.datetime.now().month > 10 else 0
    years = [i for i in range(current_year + inc, 1992, -1)]
    return years


def create_bookings_file(year, event_id):
    pass
    # directory = os.path.join(data_location, str(year))
    # filename = bookings_file(year, event_id)
    # fields = bookings_file_fields()
    # return create_wags_data_file(directory, filename, fields, access_all=True)


def create_wags_data_file(directory, filename, fields, access_all=False):
    pass
    # result = True
    # try:
    #     if not os.path.exists(directory):
    #         os.makedirs(directory)
    #     if not os.path.exists(filename):
    #         create_data_file(filename, fields, access_all)
    # except:
    #     e = sys.exc_info()[0]
    #     result = False
    # return result

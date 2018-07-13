import datetime
import os
import itertools
from operator import and_

from back_end.data_utilities import lookup, mean, first_or_default, fmt_date, in_date_range
from back_end.table import Table
from front_end.form_helpers import get_elements_from_html
from globals.enumerations import MemberStatus, PlayerStatus, EventType, Function
from models.wags_db import Event, Score, Course, CourseData, Trophy, Player, Venue, Handicap, Member, Contact, \
    Schedule, Booking, User, Committee
from globals.app_setup import db_session
from sqlalchemy import text

from globals import config
from back_end.file_access import get_records, update_html_elements, get_file_contents

# region text files
data_location = config.get('locations')['data']
html_location = config.get('locations')['html']


def accounts_file(year):
    return os.path.join(html_location, 'reports', str(year), 'accounts.tab')


def news_file():
    return os.path.join(html_location, 'news/news.htm')


def front_page_header_file():
    return os.path.join(html_location, 'header.htm')


# endregion


# region user

def get_user(id=None, user_name=None):
    if id:
        return db_session.query(User).filter(User.id == id).first()
    if user_name:
        return db_session.query(User).filter(User.user_name == user_name).first()


def save_user(user):
    if not user.id:
        db_session.add(user)
    db_session.commit()


# endregion


# region venues
def get_all_venue_names():
    return [v.name for v in db_session.query(Venue).order_by(Venue.name)]


def get_all_venues():
    venues = {}
    for venue in db_session.query(Venue).order_by(Venue.name):
        venues[venue.id] = venue
    return venues


def get_venue_select_choices():
    return [(v.id, v.name) for v in db_session.query(Venue).order_by(Venue.name)]


def get_venue(venue_id):
    if venue_id > 0:
        return db_session.query(Venue).filter(Venue.id == venue_id).first()
    else:
        return Venue()


def save_venue(venue):
    if not venue.id:
        db_session.add(venue)
    db_session.commit()
    return venue.id


def get_venue_url(venue):
    if venue.contact:
        url = '//' + venue.contact.url
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
    return db_session.query(Event).filter_by(id=event_id).first() or Event(id=0, date=datetime.date.today())


def get_event_for_course_and_date(date, course_id):
    return db_session.query(Event).filter_by(date=date, course_id=course_id).first() or Event(date=date,
                                                                                              course_id=course_id)


def get_all_events():
    return db_session.query(Event) \
        .filter(Event.date <= datetime.date.today()) \
        .order_by(Event.date.desc())


def get_event_select_list():
    return [(e.id, fmt_date(e.date) + ' ' + e.venue.name) for e in get_all_events()]


def get_events_for_year(year):
    stmt = text("select id from events where strftime('%Y', date)=:year order by date, type desc").params(
        year=str(year))
    return db_session.query(Event).from_statement(stmt)


def get_events_for_period(start, end):
    return db_session.query(Event).filter(Event.date.between(start, end))


def get_event_scores(event_id):
    event = get_event(event_id)
    head = ['player_id', 'position', 'points', 'shots', 'handicap', 'status', 'card', 'player_name']
    data = []
    for score in event.scores:
        player_state = score.player.state_as_of(event.date)
        row = [score.player_id,
               score.position,
               score.points,
               score.shots,
               player_state.handicap,
               player_state.status,
               score.card,
               score.player.full_name()]
        data.append(row)
    return Table(head, data)


def get_event_cards(event_id):
    scores = db_session.query(Score).filter(Score.event_id == event_id)
    return {s.player_id: s.card for s in scores}


def save_event_details(event_id, details):
    event_type = details['event_type']
    if event_id > 0:
        event = get_event(event_id)
    else:
        event = Event(type=event_type)
        db_session.add(event)

    event.venue_id = details['venue_id']
    event.date = details['date']
    event.trophy_id = details['trophy_id']
    event.course_id = details['course_id']
    event.organiser_id = details['organiser_id']
    event.member_price = details['member_price']
    event.guest_price = details['guest_price']
    event.booking_start = details['start_booking']
    event.booking_end = details['end_booking']
    event.max = details['max']
    event.note = details['note']

    if event_type == EventType.wags_vl_event:
        schedule = []
        for row in details['schedule']:
            if row['time'] is None:
                continue
            item = first_or_default([s for s in event.schedule if s.time == row['time']], None)
            if item:
                item.time = row['time']
                item.text = row['text']
            else:
                item = Schedule(event_id=event_id, time=row['time'], text=row['text'])
            schedule.append(item)
        event.schedule = sorted(schedule)

    if event_type == EventType.wags_tour:
        tour_events = []
        all_courses = get_all_courses()
        all_venues = get_all_venues()
        for row in details['tour_schedule']:
            course_id = first_or_default(
                [c.id for c in all_courses.values() if c.name.lower() == row['course'].lower()], None)
            venue_id = first_or_default([v.id for v in all_venues.values() if v.name.lower() == row['course'].lower()],
                                        None)
            if not venue_id:
                venue_id = all_courses[course_id].venue_id
            trophy_id = None
            item = first_or_default([s for s in event.tour_events if s.date == row['date']], None)
            if item:
                item.course_id = course_id
                item.venue_id = venue_id
                item.trophy_id = trophy_id
            else:
                item = get_event_for_course_and_date(row['date'], course_id)
                item.type = EventType.wags_vl_event
                item.tour_event_id = event_id
                item.venue_id = venue_id
                item.trophy_id = trophy_id
            tour_events.append(item)
        event.tour_events = tour_events
    db_session.commit()
    return event.id


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
        update_event_winner(event, result)
    else:
        event.winner_id = event.average_score = None
    event.scores = scores
    db_session.commit()
    if event.tour_event:
        if event.tour_event.trophy and event in event.tour_event.tour_events:
            update_tour_winner(event.tour_event)


def update_event_winner(event, result):
    event.average_score = mean(result.get_columns('points'))

    def sel_fn(values):
        return values['status'] == str(MemberStatus.full_member.value)

    result = result.select_rows(sel_fn)
    event.winner_id = int(result.get_columns('player_id')[0])


def update_tour_winner(event):
    pass
    # result = get_tour_results(event)
    # event.winner_id = int(result.get_columns('player_id')[0])


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


def get_players_for_event(event):
    if event.tour_event_id:
        if len(event.tour_event.bookings) > 0:
            event = event.tour_event
    players = []
    if len(event.bookings) > 0:
        for member in event.bookings:
            players.append(member.member.player)
            for guest in member.guests:
                p = get_player_by_name(guest.name)
                if p:
                    state = p.state_as_of(event.date)
                    if state.handicap != guest.handicap:
                        p.handicaps.append(
                            Handicap(date=event.date, status=PlayerStatus.guest, handicap=guest.handicap))
                else:
                    p = add_player(guest.name, guest.handicap, PlayerStatus.guest, event.date)
                players.append(p)
    else:
        players = [s.player for s in event.scores]
    return players


def sorted_players_for_event(event):
    players = get_players_for_event(event)

    def getKey(player):
        score = player.score_for(event.id)
        return score.position if score.points > 0 else 99, player.last_name, player.first_name

    return sorted(players, key=getKey)


def normalise_name(all_names, name):
    i = lookup(all_names, name, case_sensitive=False)
    if i == -1:
        return name.title(), i
    else:
        return all_names[i], i


def get_results(event, for_edit_hcap=False):
    '''Returns all results for an event. Adds any players that were booked but without any recorded scores yet.'''
    players = []
    results = []
    state_date = datetime.date.today() if for_edit_hcap else event.date
    for score in [s for s in event.scores]:
        player = score.player
        state = player.state_as_of(state_date)
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
    bookings = event.bookings
    booked = get_players_for_event(event, for_edit_hcap)
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


def is_event_result_editable(event):
    override = config.get('override')
    return override or (datetime.date.today() > event.date) and (datetime.date.today().year == event.date.year)


def is_last_event(event):
    last = get_last_event(event.date.year)
    override = config.get('override')
    return override or event.id == last.id


def is_event_editable(year):
    override = config.get('override')
    return override or year >= datetime.date.today().year


def is_event_bookable(event):
    # result:  1 - booking open, 0 - booking closed, -1 - booking not applicable
    if event.booking_start:
        booking_start = event.booking_start
        booking_end = event.booking_end
        in_range = in_date_range(datetime.date.today(), booking_start, booking_end)
    else:
        in_range = False
    event_type = event.type
    if event.tour_event_id or event_type == EventType.non_event:
        return -1
    override = config.get('override')
    return 1 if override or in_range else 0


def get_last_event(year=None, include_tours=False):
    today = datetime.date.today()
    if not year:
        year = today.year
    past = [e for e in get_events_for_year(year) if e.type == EventType.wags_vl_event and e.date <= today]
    if len(past) > 0:
        if include_tours and past[-1].tour_event:
            return past[-1].tour_event
        else:
            return past[-1]
    return get_last_event(year - 1)


def get_next_event(year=None):
    today = datetime.date.today()
    if not year:
        year = today.year
    future = [e for e in get_events_for_year(year) if e.type == EventType.wags_vl_event and e.date >= today]
    for event in future:
        if not event.tour_event:
            return event
    return None


def get_events_in(date_range):
    events = db_session.query(Event).filter(and_(Event.date >= date_range[0], Event.date <= date_range[1])).all()
    return events


# endregion


# region tours
def is_tour_event(event):
    pass
    # return (not is_num(event['num'])) or float(event['num']) > math.floor(float(event['num']))


def get_tour_scores(event_ids):
    ids = '(' + (','.join([str(id) for id in event_ids])) + ')'
    s = text("select * from scores where event_id in {} order by player_id, event_id".format(ids))
    scores = []
    for score in db_session.query(Score).from_statement(s):
        status = score.player.state_as_of(score.event.date).status
        scores.append(
            [score.event.date, score.event_id, score.player_id, score.points, score.event.trophy, status.value])
    head = ['date', 'event', 'player', 'points', 'trophy', 'status']
    return head, scores


# endregion


# region courses
def get_course_select_choices():
    return [(c.id, c.name) for c in db_session.query(Course).order_by(Course.name)]


def get_all_course_names():
    return [c.name for c in db_session.query(Course).order_by(Course.name)]


def get_all_courses():
    courses = {}
    for course in db_session.query(Course).order_by(Course.name):
        courses[course.id] = course
    return courses


def get_course(course_id):
    if course_id > 0:
        return db_session.query(Course).filter(Course.id == course_id).first()
    else:
        return Course()


def lookup_course(course):
    course_id = db_session.query(Course.id).filter(Course.name == course).first()
    return course_id.id


def get_course_data(course_id, year):
    stmt = text("select * from course_data where course_id=:course_id and year>=:year order by year")
    stmt = stmt.columns(CourseData.course_id, CourseData.year, CourseData.sss, CourseData.si, CourseData.par)
    return db_session.query(CourseData).from_statement(stmt).params(course_id=course_id, year=year).first()


def save_course(course_id, data):
    year = data['year']
    if course_id > 0:
        course = get_course(course_id)
    else:
        course = Course()
        course.cards = [CourseData(year=year)]
        db_session.add(course)
    course.name = data['name']
    course.venue_id = data['venue_id']
    card = course.course_data_as_of(year)
    card.year = year
    card.sss = data['sss']
    card.si = data['si']
    card.par = data['par']

    db_session.commit()


def save_course_card(course_id, year, fields, data):
    pass
    # course_id = coerce(course_id, str)
    # new = dict(zip(['course', 'year'] + fields, [course_id, year] + data))
    # update_record(course_data_file(), ['course', 'year'], new)


# endregion


# region players

def get_all_players():
    return db_session.query(Player).order_by(Player.last_name, Player.first_name)


def get_player(player_id):
    return db_session.query(Player).filter(Player.id == player_id).first()


def get_player_by_name(player_name):
    all_players = get_all_players()
    all_player_names = [p.full_name() for p in all_players]
    name, i = normalise_name(all_player_names, player_name)
    if i >= 0:
        return all_players[i]
    else:
        return None


def get_player_names_as_dict(player_ids):
    ids = '(' + (','.join([str(id) for id in player_ids])) + ')'
    s = text("select * from players where id in {}".format(ids))
    players = {}
    for player in db_session.query(Player).from_statement(s):
        players[player.id] = player.full_name()
    return players


def get_player_names(player_ids):
    players = get_player_names_as_dict(player_ids)
    return [players[id] for id in player_ids]


def get_player_id(player_name):
    all_players = get_all_players()
    all_player_names = [p.full_name() for p in all_players]
    name, i = normalise_name(all_player_names, player_name)
    if i >= 0:
        return all_players[i].id
    else:
        return 0


def get_players_as_of(date, status):
    res = []
    for p in get_all_players():
        state = p.state_as_of(date)
        if state.status == status:
            res.append(p)
    return res


def add_player(name, hcap, status, date, commit=True):
    first, last = name.split(' ')
    player = Player(first_name=first, last_name=last)
    player.handicaps.append(Handicap(date=date, handicap=hcap, status=status))
    db_session.add(player)
    if commit:
        db_session.commit()
    return player


def save_handicaps(new_table):
    if len(new_table.data) == 0:
        return
    players = set(new_table.get_columns('player_id'))
    dates = set(new_table.get_columns('date'))
    current = db_session.query(Handicap).filter(Handicap.date.in_(dates), Handicap.player_id.in_(players)).all()
    for record in new_table.data:
        new = dict(zip(new_table.head, record))
        hcap = first_or_default([h for h in current if h.player_id == new['player_id'] and h.date == new['date']], None)
        if hcap:
            hcap.handicap = new['handicap']
            hcap.status = new['status']
        else:
            hcap = Handicap(player_id=new['player_id'],
                            date=new['date'],
                            handicap=new['handicap'],
                            status=new['status'])
        db_session.add(hcap)
    db_session.commit()


# endregion


# region Members
def get_member(member_id):
    return db_session.query(Member).filter_by(id=member_id).first()


def get_member_by_email(email):
    contact = db_session.query(Contact).filter_by(email=email).first()
    if contact:
        return db_session.query(Member).filter_by(contact_id=contact.id).first()
    else:
        return None


def get_all_members(current=True):
    if current:
        return db_session.query(Member) \
            .filter(Member.status.in_([MemberStatus.full_member, MemberStatus.overseas_member]))
    else:
        return db_session.query(Member)


def get_current_members_as_players(current=True):
    members = get_all_members(current)
    players = [m.player for m in members]

    def sk(player):
        return player.last_name.lower() + player.first_name.lower()

    players.sort(key=sk)
    return players


def get_member_select_choices(current=False):
    choices = [(p.member.id, p.full_name()) for p in get_current_members_as_players(current=current)]
    return choices


def save_member(member_id, data):
    new_member = member_id == 0
    name = data['first_name'] + ' ' + data['last_name']
    orig_name = data['orig_name']
    handicap = data['handicap']
    status = data['status']
    player_id = get_player_id(name if new_member else orig_name)
    date = data['as_of']

    # set player status and handicap
    if status in [MemberStatus.full_member, MemberStatus.overseas_member]:
        player_status = PlayerStatus.member
    else:
        player_status = PlayerStatus.ex_member
    if player_id == 0:
        player = add_player(name, handicap, player_status, date, commit=False)
    else:
        player = get_player(player_id)
        if name != orig_name:
            player.first_name = data['first_name']
            player.last_name = data['last_name']

        if handicap != data['orig_handicap'] or status.value != data['orig_status']:
            state = first_or_default([s for s in player.handicaps if s.date == date], None)
            if state:
                state.handicap = handicap
                state.status = player_status
            else:
                state = Handicap(date=date, status=player_status, handicap=handicap)
                player.handicaps.append(state)
    # create/update member
    contact = Contact(
        email=data['email'],
        address=data['address'],
        post_code=data['post_code'],
        phone=data['phone']
    )
    if new_member:
        member = Member(
            player=player,
            contact=contact,
            status=status,
            proposer_id=data['proposer_id']
        )
    else:
        member = get_member(member_id)
        member.contact = contact
        member.player = player
        member.status = status
        member.proposer_id = data['proposer_id']
    if status.value != data['orig_status']:
        if status == MemberStatus.full_member:
            member.accepted = date
        elif status in (MemberStatus.ex_member, MemberStatus.rip):
            member.resigned = date

    db_session.commit()


def save_member_details(member_id, data):
    member = get_member(member_id)
    player = member.player
    contact = member.contact
    player.first_name = data['first_name']
    player.last_name = data['last_name']
    contact.email = data['email']
    contact.address = data['address']
    contact.post_code = data['post_code']
    contact.phone = data['phone']
    db_session.commit()


def get_member_account(member_name, year):
    file = accounts_file(year)
    return Table(*get_records(file, 'member', member_name))


# endregion


# region Trophies
def get_trophy_select_choices():
    return [(t.id, t.name) for t in db_session.query(Trophy).order_by(Trophy.name)]


def get_all_trophy_names():
    return [t.name for t in db_session.query(Trophy).order_by(Trophy.name)]


def get_trophy(trophy_id):
    return db_session.query(Trophy).filter_by(id=trophy_id).first()


# endregion


# region Scores

def get_scores_for_player(player_id, year=None):
    player = get_player(player_id)
    scores = player.scores
    head = ['date', 'course', 'player_id', 'position', 'shots', 'points', 'handicap', 'status']
    res = Table(head, [extract_score_data(s) for s in scores])
    if year:
        def lu_fn(values):
            return values['date'].year == year

        res = res.where(lu_fn)
    return res


def extract_score_data(score):
    date = score.event.date
    state = score.player.state_as_of(date)
    return [date,
            score.event.course.name,
            score.player_id,
            score.position,
            score.shots,
            score.points,
            state.handicap,
            state.status]


def get_scores(year=None, status=None, player_id=None):
    if year:
        start = datetime.date(year, 1, 1)
        end = min(datetime.date(year, 12, 31), datetime.date.today())
        events = get_events_for_period(start, end)
    else:
        events = db_session.query(Event)
    scores = [e.scores for e in events]
    if status:
        scores = [s for ls in scores for s in ls if s.player.state_as_of(s.event.date).status == status]
    if player_id:
        scores = [s for ls in scores for s in ls if s.player.id == player_id]

    head = ['date', 'course', 'player_id', 'position', 'shots', 'points', 'handicap', 'status']
    return Table(head, [extract_score_data(s) for s in scores])


def get_all_scores():
    current_members = get_all_members(current=True)
    current_players = [m.player_id for m in current_members]
    scores = db_session.query(Score.player_id, Event.date) \
        .join(Event) \
        .filter(Score.player_id.in_(current_players)) \
        .order_by(Score.player_id, Event.date) \
        .all()
    head = ['player_id', 'player', 'status', 'count', 'first_game']
    data = []
    for player_scores in [list(group) for key, group in itertools.groupby(scores, lambda x: x[0])]:
        player_id, first = player_scores[0]
        status = [m.status for m in current_members if m.player_id == player_id]
        count = len(player_scores)
        player = get_player(player_id)
        data.append((player_id, player.full_name(), status[0].name, count, fmt_date(first)))
    res = Table(head, data)
    res.sort('count', reverse=True)
    return res


# endregion


# region Bookings
def get_booking(event_id, member_id):
    return db_session.query(Booking).filter_by(event_id=event_id, member_id=member_id).first() \
            or Booking(event_id=event_id, member_id=member_id, date=datetime.date.today())


def get_all_bookings(event_id):
    return db_session.query(Booking).filter_by(event_id=event_id)


def save_booking(booking):
    # if not booking.id:
    #     db_session.add(booking)
    db_session.commit()


# endregion


def get_all_years():
    current_year = datetime.datetime.now().year
    inc = 1 if datetime.datetime.now().month > 10 else 0
    years = [i for i in range(current_year + inc, 1992, -1)]
    return years


def get_committee():
    return db_session.query(Committee).filter(Committee.function < Function.Captain).all()


def get_committee_function(function):
    return db_session.query(Committee).filter_by(function=function).first()


def update_front_page(items):
    update_html_elements(front_page_header_file(), items)


def get_front_page_items(items):
    html = get_file_contents(front_page_header_file())
    return get_elements_from_html(html, items)

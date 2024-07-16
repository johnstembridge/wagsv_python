import datetime
import os
import itertools

from back_end.file_access import get_records, update_html_elements, get_file_contents, create_data_file
from back_end.data_utilities import mean, first_or_default, parse_float, normalise_name, gen_to_list, fmt_date, \
    my_round, coerce
from back_end.table import Table
from back_end.calc import calc_stableford_points, calc_swings, calc_positions

from globals.enumerations import MemberStatus, PlayerStatus, EventType, Function
from globals.app_setup import db
from globals import config

from front_end.form_helpers import get_elements_from_html

from models.wags_db import Event, Score, Course, CourseData, Trophy, Player, Venue, Handicap, Member, Contact, \
    Schedule, Booking, User, Committee, Role
from sqlalchemy import text, and_, func

db_session = db.session

# region text files
data_location = config.get('locations')['data']
html_location = config.get('locations')['html']


def accounts_file(year):
    path = os.path.join(html_location, 'reports', str(year))
    if not os.path.exists(path):
        os.mkdir(path, 755)
        fields = ['Member', 'Date', 'Item', 'Debit', 'Credit']
        create_data_file(os.path.join(path, 'accounts.tab'), fields)
    return os.path.join(path, 'accounts.tab')


def news_file():
    return os.path.join(html_location, 'news/news.htm')


def front_page_header_file():
    return os.path.join(html_location, 'front/header.htm')


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
    return gen_to_list(db_session.query(Event).filter(Event.date.between(start, end)).order_by(Event.date))


def get_events_for_course(course_id, period=None):
    if period:
        res = db_session.query(Event) \
            .filter(and_(Event.course_id == course_id, Event.date.between(period[0], period[1]))) \
            .order_by(Event.date)
    else:
        res = db_session.query(Event).filter(Event.course_id == course_id).order_by(Event.date)
    return gen_to_list(res)


def get_event_scores(event_id):
    event = get_event(event_id)
    head = ['player_id', 'position', 'points', 'shots', 'handicap', 'status', 'card', 'player_name', 'first_name',
            'last_name', 'whs']
    data = []
    for score in event.scores:
        player_state = score.player.state_as_of(event.date)
        row = [score.player_id,
               score.position,
               score.points,
               score.shots,
               player_state.playing_handicap(event),
               player_state.status,
               score.card,
               score.player.full_name(),
               score.player.first_name,
               score.player.last_name,
               player_state.handicap]
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
    event.members_only = details['members_only']
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

    if event_type in [EventType.wags_tour, EventType.minotaur]:
        tour_events = []
        all_courses = get_all_courses()
        for row in details['tour_schedule']:
            date = row['date']
            course_id = row['course']
            if course_id > 0:
                venue_id = all_courses[course_id].venue_id
            else:
                venue_id = event.venue_id
            item = first_or_default([s for s in event.tour_events if s.date == date], None)
            if item:
                item.course_id = course_id
                item.venue_id = venue_id
            #
            else:
                item = get_event_for_course_and_date(date, course_id)
                item.type = EventType.wags_vl_event
                item.tour_event_id = event_id
                item.venue_id = venue_id
            tour_events.append(item)
        event.tour_events = tour_events
    db_session.commit()
    return event.id


def save_event_result(event_id, result):
    event = get_event(event_id)
    scores = []
    whs = {}
    delete = {s.id: True for s in event.scores}
    for row in result.rows():
        score = first_or_default([s for s in event.scores if s.player_id == int(row['player_id'])], None)
        if score:
            score.position = row['position']
            score.shots = row['shots']
            score.points = row['points']
            if 'card' in row:
                score.card = row['card']
            if score.id in delete:
                delete[score.id] = False
        else:
            score = Score(event_id=event_id,
                          player_id=row['player_id'],
                          position=row['position'],
                          shots=row['shots'],
                          points=row['points'],
                          card=row.get('card', None)
                          )
        scores.append(score)
        whs[int(row['player_id'])] = float(row['whs'])
    for score in event.scores:
        if delete.get(score.id, False):
            db_session.delete(score)
        else:
            # add handicap for player if necessary
            player = get_player(score.player_id)
            state = player.state_as_of(event.date)
            if state.handicap == 0 or not state.status.current_member() and state.date < event.date:
                player.handicaps.append(
                    new_handicap(player, status=state.status, handicap=whs[player.id], date=event.date))
    if len(result.data) > 0:
        update_event_winner(event, result)
    else:
        event.winner_id = event.average_score = None
    event.scores = scores
    if event.tour_event:
        if event.tour_event.trophy and event in event.tour_event.tour_events:
            update_tour_winner(event.tour_event)
    db_session.commit()


def save_event_booking(event_id, new_bookings):
    event = get_event(event_id)
    bookings = []
    delete = {b.id: True for b in event.bookings}
    for row in new_bookings.rows():
        booking = first_or_default([b for b in event.bookings if b.id == int(row['booking_id'])], None)
        if booking:
            booking.playing = row['playing']
            if row['hcap']:
                if booking.guests:
                    # reset guest name and handicap or remove guest if not playing
                    guest_booking = first_or_default([b for b in booking.guests if b.id == int(row['guest_id'])], None)
                    if guest_booking:
                        guest_booking.name = row['name']
                        guest_booking.handicap = float(row['hcap'])
                        if not row['playing']:
                            db_session.delete(guest_booking)
            if booking.id in delete:
                delete[booking.id] = False
        bookings.append(booking)
    for booking in event.bookings:
        if delete.get(booking.id, False):
            db_session.delete(booking)
    event.bookings = bookings
    db_session.commit()


def update_event_winner(event, result):
    event.average_score = mean([x for x in result.get_columns('points') if x > 0])

    def sel_fn(values):
        return values['status'] == PlayerStatus.member

    result = result.select_rows(sel_fn)
    if len(result.data) > 0:
        event.winner_id = int(result.get_columns('player_id')[0])


def update_tour_winner(event):
    result = get_tour_results(event)
    event.winner_id = int(result.get_columns('player_id')[0])


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


def get_players_for_event_id(event_id):
    return get_players_for_event(get_event(event_id))


def get_players_for_event(event):
    if event.tour_event_id:
        if len(event.tour_event.bookings) > 0:
            event = event.tour_event
    players = []
    if len(event.bookings) > 0:
        for member in event.bookings:
            if member.playing:
                players.append(member.member.player)
            for guest in member.guests:
                p = get_player_by_name(guest.name)
                if p:
                    state = p.state_as_of(event.date)
                    if state.status in [PlayerStatus.guest, PlayerStatus.ex_member]:
                        if state.handicap != guest.handicap:
                            p.handicaps.append(
                                Handicap(date=event.date, status=state.status, handicap=guest.handicap))
                    else:
                        guest.handicap = state.handicap
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


def is_latest_event(event):
    last = get_latest_event()
    override = config.get('override')
    return override or event.id == last.id


def get_latest_event(include_tours=False):
    today = datetime.date.today()
    year = today.year
    previous = [e for e in get_events_for_year(year) if e.type == EventType.wags_vl_event and e.date <= today]
    if len(previous) == 0:
        previous = [e for e in get_events_for_year(year - 1) if e.type == EventType.wags_vl_event]
    if include_tours and previous[-1].tour_event:
        return previous[-1].tour_event
    else:
        return previous[-1]


def get_next_event(date=datetime.date.today()):
    start = date + datetime.timedelta(days=1)
    end = datetime.date(date.year, 12, 31)
    next = first_or_default(get_events_in((start, end)), None)
    if not next:
        end = datetime.date(date.year + 1, 12, 31)
        next = first_or_default(get_events_in((start, end)), None)
    return next


def get_events_in(date_range):
    events = db_session.query(Event) \
        .filter(Event.date.between(date_range[0], date_range[1]), Event.type == EventType.wags_vl_event) \
        .order_by(Event.date).all()
    return events


def is_event_list_editable(year):
    override = config.get('override')
    return override or year >= datetime.date.today().year


# endregion


# region tours
def get_tour_results(event):
    trophy = event.trophy
    event_ids = [v.id for v in event.tour_events]
    dates = {v.id: v.date for v in event.tour_events}
    multi = len([v for v in event.tour_events if v.trophy == trophy]) > 0
    scores = Table(*get_tour_scores(event_ids))
    res = []
    for player_id, event_scores in scores.group_by('player'):
        s = [s for s in event_scores]
        status = s[0][5]
        missing = list(set(event_ids).difference(set([x[1] for x in s])))  # event ids
        for m in missing:
            s.append([dates[m], m, 0, 0, None, 0])
        s.sort()
        p = [int(x[3]) for x in s]  # points
        if trophy and multi:
            tp = sum([int(x[3]) for x in s if x[4] == trophy])  # total points for trophy
        else:
            tp = sum(p)

        r = (player_id, status, p, tp)
        res.append(r)
    head = ['player_id', 'status', 'scores', 'total']
    res = Table(head, res)
    res.sort(['total'], reverse=True)
    res.add_column('position', calc_positions(res.get_columns('total')))
    return res


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


def save_course(course):
    if not course.id:
        db_session.add(course)
    db_session.commit()


def lookup_course(course):
    course_id = db_session.query(Course.id).filter(Course.name == course).first()
    return course_id.id


def get_course_data(course_id, year):
    cd = db_session.query(CourseData).filter(and_(CourseData.course_id == course_id, CourseData.year == year)).first()
    if not cd:
        cd = CourseData()
    return cd


def save_course_data(course_id, data):
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


def new_handicap(player, status, handicap, date):
    return Handicap(player_id=player.id, status=status, handicap=handicap, date=date)


def save_handicaps(new_table):
    if len(new_table.data) == 0:
        return
    players = set(new_table.get_columns('player_id'))
    dates = set(new_table.get_columns('date'))
    current = db_session.query(Handicap).filter(Handicap.date.in_(dates), Handicap.player_id.in_(players)).all()
    for new in new_table.rows():
        hcap = first_or_default([h for h in current if h.player_id == new['player_id'] and h.date == new['date']], None)
        if hcap:
            if (hcap.handicap == new['handicap'] and hcap.status == new['status']):
                continue
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
    member = db_session.query(Member).filter_by(id=member_id).first()
    return member


def get_member_by_email(email):
    # case-insensitive
    contact = db_session.query(Contact).filter(func.lower(Contact.email) == func.lower(email)).first()
    if contact:
        return db_session.query(Member).filter_by(contact_id=contact.id).first()
    else:
        return None


def get_member_by_name(name):
    name = name.split(' ')
    player = db_session.query(Player).filter_by(first_name=name[0], last_name=name[1]).first()
    if player:
        return db_session.query(Member).filter_by(player_id=player.id).first()
    else:
        return None


def get_members_by_status(status):
    members = db_session.query(Member).filter_by(status=status)
    return members


def get_all_members(current=True):
    if current:
        return db_session.query(Member) \
            .filter(Member.status.in_([MemberStatus.full_member, MemberStatus.overseas_member]))
    else:
        return db_session.query(Member)


def get_current_members_as_players(current=True):
    members = get_all_members(current)
    players = [m.player for m in members]

    def lastname_firstname(player):
        return player.last_name.lower() + player.first_name.lower()

    players.sort(key=lastname_firstname)
    return players


def get_member_select_choices(current=False):
    choices = [(p.member.id, p.full_name()) for p in get_current_members_as_players(current=True)]
    return choices


def save_member(member_id, data):
    new_member = member_id == 0
    name = data['first_name'] + ' ' + data['last_name']
    orig_name = data['orig_name']
    handicap = data['handicap']
    status = data['status']
    player_id = get_player_id(name if new_member else orig_name)
    date = data['as_of'] or data['accepted']
    access = data['access']

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
    if new_member:
        contact = Contact(
            email=data['email'],
            address=data['address'],
            post_code=data['post_code'],
            phone=data['phone']
        )
        member = Member(
            player=player,
            contact=contact,
            status=status,
            proposer_id=data['proposer_id'],
            accepted=data['accepted']
        )
    else:
        member = get_member(member_id)
        member.contact.email = data['email']
        member.contact.address = data['address']
        member.contact.post_code = data['post_code']
        member.contact.phone = data['phone']
        member.player = player
        member.status = status
        member.proposer_id = data['proposer_id']
    if status.value != data['orig_status']:
        if status == MemberStatus.full_member:
            member.accepted = date
        elif status in (MemberStatus.ex_member, MemberStatus.rip):
            member.resigned = date
    else:
        member.accepted = data['accepted']
    if member.user:
        if not access in [r.role for r in member.user.roles]:
            member.user.roles.append(Role(user_id=member.user.id, role=access))
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


def member_account_balance(member_id, year):
    member = get_member(member_id)
    balance = 0
    account = get_member_account(member.player.full_name(), year)
    for item in account.rows():
        debit = parse_float(item['debit'])
        credit = parse_float(item['credit'])
        balance += (credit or 0) - (debit or 0)
    return balance


# endregion


# region Trophies
def get_trophy_select_choices():
    return [(t.id, t.name) for t in db_session.query(Trophy).order_by(Trophy.name)]


def get_trophy(trophy_id):
    return db_session.query(Trophy).filter_by(id=trophy_id).first()


# endregion


# region Scores

def get_scores_for_player(player_id, year=None):
    player = get_player(player_id)
    if year:
        scores = [s for s in player.scores if s.event.type == EventType.wags_vl_event and s.event.date.year == year]
    else:
        scores = [s for s in player.scores if s.event.type == EventType.wags_vl_event and s.points > 0]
    head = ['date', 'course', 'player_id', 'position', 'shots', 'points', 'handicap', 'status']
    res = Table(head, [extract_score_data(s) for s in scores])
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
            state.playing_handicap(score.event),
            state.status]


def get_scores(year=None, status=None, player_id=None):
    if year:
        start = datetime.date(year, 1, 1)
        end = min(datetime.date(year, 12, 31), datetime.date.today())
        events = get_events_for_period(start, end)
    else:
        events = db_session.query(Event)
    scores = [e.scores for e in events if e.type == EventType.wags_vl_event]
    if status:
        scores = [s for ls in scores for s in ls if s.player.state_as_of(s.event.date).status == status]
    if player_id:
        scores = [s for ls in scores for s in ls if s.player.id == player_id]
    scores = [s for s in scores if s.player.member.qualifying_date() <= s.event.date]
    head = ['date', 'course', 'player_id', 'position', 'shots', 'points', 'handicap', 'status']
    return Table(head, [extract_score_data(s) for s in scores])


def get_all_scores():
    current_members = get_all_members(current=True)
    current_players = [m.player_id for m in current_members]
    scores = db_session.query(Score.player_id, Event.date) \
        .join(Event) \
        .filter(Score.player_id.in_(current_players)) \
        .filter(Score.points > 0) \
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


def save_booking(booking):
    if not booking.id:
        db_session.add(booking)
    db_session.commit()


# endregion


# region Reports

def get_vl(year):
    scores = get_scores(year=year, status=PlayerStatus.member)
    scores.sort(['player_id', 'date'])
    vl = Table(['player_id', 'points', 'events', 'lowest'],
               [vl_summary(scores.column_index('points'), key, list(values))
                for key, values in scores.group_by('player_id')])
    vl.sort(['points', 'lowest'], reverse=True)
    vl.add_column('position', calc_positions(vl.get_columns('points')))
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
        cards = {s.player_id: s.card for s in event.scores}
        # cards = get_event_cards(event_id)
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
        swings.extend(calc_swings(event))
    swings = Table(header, swings)
    swings.sort('swing', reverse=True)
    swings.top_n(10)
    swings.add_column('position', calc_positions(swings.get_columns('swing')))
    year_range = [first.year, first.year + 1]
    return year_range, swings


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


def suspend_flush():
    return db_session.no_autoflush

from enum import Enum


class FormEnum(Enum):
    @classmethod
    def choices(cls, all=False):
        return [(choice, choice.name.replace('_', ' ')) for choice in cls]

    @classmethod
    def coerce(cls, item):
        return cls(int(item)) if not isinstance(item, cls) else item

    def __str__(self):
        return str(self.value)


class PlayerStatus(FormEnum):
    guest = 0
    member = 1
    ex_member = 2
    new = 3
    non_vl = 4

    def qualify(self):
        # for appending to player name in a list
        if self != PlayerStatus.member:
            qual = " (" + self.name + ")"
        else:
            qual = ""
        return qual

    def current_member(self):
        return self in [PlayerStatus.member, PlayerStatus.new, PlayerStatus.non_vl]


class MemberStatus(FormEnum):
    full_member = 1
    overseas_member = 2
    ex_member = 3
    rip = 4


class EventType(FormEnum):
    cancelled = -1
    non_event = 0
    wags_vl_event = 1
    wags_tour = 2
    non_vl_event = 3
    minotaur = 4

    def long_description(self):
        if self == EventType.cancelled:
            return 'Event cancelled'
        if self == EventType.non_event:
            return 'Non WAGS event'
        if self == EventType.wags_vl_event:
            return 'VL event'
        if self == EventType.non_vl_event:
            return 'Non VL event'
        if self == EventType.wags_tour:
            return 'WAGS tour'
        if self == EventType.minotaur:
            return 'WAGS Minotaur'


class EventBooking(FormEnum):
    viewable = 0
    open = 1
    not_applicable = -1
    cancelled = -2


class NewsItemType(FormEnum):
    open_booking = 0
    event_result = 1
    handicap_update = 2
    account_update = 3
    publish_minutes = 4


class UserRole(FormEnum):
    user = 1
    admin = 2


class Function(FormEnum):
    Chairman = 1
    Communications = 2
    Fixtures = 3
    Handicaps = 4
    Membership = 5
    Merchandise = 6
    Secretary = 7
    Treasurer = 8
    Website = 9
    Captain = 10
    Design = 11


class MinutesType(FormEnum):
    all = 0
    Committee = 1
    AGM = 2


class HandicapRegime(FormEnum):
    wags0 = 0       # straight handicap
    wags1 = 1       # apply slope factor
    wags2 = 2       # apply slope factor, take 95%
    wags3 = 3       # apply slope factor, course rating and par, take 95%

    @classmethod
    def regime_for_year(cls, year):
        wags_version_1_year = 2021
        wags_version_2_year = 2023
        wags_version_3_year = 3000
        if year < wags_version_1_year:
            return HandicapRegime.wags0
        if year in range(wags_version_1_year, wags_version_2_year):
            return HandicapRegime.wags1
        if year in range(wags_version_2_year, wags_version_3_year):
            return HandicapRegime.wags2
        else:
            return HandicapRegime.wags3

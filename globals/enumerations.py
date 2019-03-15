from enum import Enum


class FormEnum(Enum):
    @classmethod
    def choices(cls):
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


class MemberStatus(FormEnum):
    full_member = 1
    overseas_member = 2
    ex_member = 3
    rip = 4


class EventType(FormEnum):
    non_event = 0
    wags_vl_event = 1
    wags_tour = 2
    non_vl_event = 3


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
    Committee = 1
    AGM = 2

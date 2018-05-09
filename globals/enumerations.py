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


class MemberStatus(FormEnum):
    full_member = 1
    overseas_member = 2
    ex_member = 3
    rip = 4


class PlayerStatus(FormEnum):
    guest = 0
    member = 1
    ex_member = 2


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

from enum import Enum


class FormEnum(Enum):
    @classmethod
    def choices(cls):
        return [(choice, choice.name) for choice in cls]

    @classmethod
    def coerce(cls, item):
        return cls(int(item)) if not isinstance(item, cls) else item

    def __str__(self):
        return str(self.value)


class MemberStatus(FormEnum):
    full_member = 1
    overseas_member = 2
    ex_member = 3


class PlayerStatus(FormEnum):
    guest = 0
    member = 1
    ex_member = 2


class EventType(FormEnum):
    non_event = 0
    wags_vl_event = 1
    wags_tour = 2
    non_vl_event = 3

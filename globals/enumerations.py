from enum import Enum


class MemberStatus(Enum):
    full_member = 1
    overseas_member = 2
    ex_member = 3


class PlayerStatus(Enum):
    guest = 0
    member = 1
    ex_member = 2


class EventType(Enum):
    non_event = 0
    wags_vl_event = 1
    wags_tour = 2
    non_vl_event = 3

from enum import Enum


class PlayerStatus:
    member = 0
    guest = 1
    ex_member = 2


class EventType(Enum):
    non_event = 0
    wags_vl_event = 1
    wags_tour = 2
    non_vl_event = 3

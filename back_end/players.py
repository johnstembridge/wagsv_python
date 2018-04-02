import os
from operator import itemgetter

from globals import config

from back_end.data_utilities import lookup, sort_name_list
from back_end.file_access import get_all_records, get_field

# data_location = r'D:\python\wagsv\data'
_data_location = config.get('locations')['data']
_players_data = r'players.tab'
_members_data = r'members.csv'
_vl_data = r'victor.tab'


class Player:

    def __init__(self, player_id):
        self.player_id = player_id
        name = Players().get_all_players()[player_id - 1]
        self.name = self.normalise_name(name)
        self.guest = None

    def as_json(self):
        data = {'player_id': self.player_id,
                'name': self.name,
                'guest': self.guest
                }
        return data

    @staticmethod
    def normalise_name(name):
        member_keys, all_members = Players().get_all_members()
        ni = lookup(member_keys, ['first_name', 'surname'])
        member_names = [' '.join(itemgetter(*ni)(m)) for m in all_members]
        mi = lookup(member_names, name.title())
        if mi < 0:
            short_name = name
        else:
            si = lookup(member_keys, ['salutation', 'surname'])
            short_name = ' '.join(itemgetter(*si) (all_members[mi]))
        return short_name


class Borg:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class Players(Borg):
    def __init__(self):
        Borg.__init__(self)

    _all_players = []
    _member_keys = []
    _all_members = []

    def member_details(self, player_id):
        pass

    def get_all_players(self):
        if len(self._all_players) == 0:
            players_file = os.path.join(_data_location, _players_data)
            with open(players_file) as f:
                self._all_players = f.read().splitlines()
        return self._all_players

    def get_all_members(self):
        if len(self._all_members) == 0:
            members_file = os.path.join(_data_location, _members_data)
            self._member_keys, self._all_members = get_all_records(members_file)
        return self._member_keys, self._all_members

    def get_current_members(self):
        all = self.get_all_players()
        vl_file = os.path.join(_data_location, _vl_data)
        pi = [int(p) - 1 for p in get_field(vl_file, 'player')]
        current = itemgetter(*pi)(all)
        return sort_name_list(current)

    def name_to_id(self, names):
        all = self.get_all_players()
        res = lookup(all, names)
        if type(names) is list:
            res = [1 + r for r in res]
        else:
            res = res + 1
        return res

    def id_to_name(self, ids):
        all = self.get_all_players()
        if type(ids) is list:
            res = [all[int(p) - 1] for p in ids]
        else:
            res = all[int(ids - 1)]
        return res


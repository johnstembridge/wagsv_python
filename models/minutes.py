import os
from globals import config
from globals.config import url_for_html
from back_end.data_utilities import fmt_date, parse_date, force_list
from globals.enumerations import MinutesType

minutes_location = config.get('locations')['minutes']


class Minutes:

    def __init__(self, type=None, date=None, file_type='pdf'):
        self.type = type
        self.date = date
        self.file_type = file_type

    def file_name(self):
        meeting_date = fmt_date(self.date).replace('/', ' ')
        meeting_type = Minutes.map_type_to_file(self.type)
        return meeting_type + ' ' + meeting_date + '.' + self.file_type

    def file_link(self, draft=False):
        draft = 'drafts' if draft else ''
        return url_for_html('minutes', draft, self.file_name())

    def full_type(self):
        if self.type == MinutesType.Committee:
            return 'Committee meeting'
        if self.type == MinutesType.AGM:
            return 'AGM'

    @staticmethod
    def file_path(draft=False):
        draft = 'drafts' if draft else ''
        return os.path.join(minutes_location, draft)

    @staticmethod
    def get_minutes(type, date):
        files = os.listdir(minutes_location)
        minutes = [
            Minutes(Minutes.map_file_to_type(f[:3]), parse_date(f[-14:-4], ' '), f[-3:])
            for f in files
            if not os.path.isdir(f) and f[:3] in Minutes.map_type_to_file(type)
        ]
        minutes = [m for m in minutes if m.date == date]
        if len(minutes) == 1:
            return minutes[0]

    @staticmethod
    def get_all_minutes(type=None, year=None):
        if not type:
            type = [t for t in MinutesType]
        type = [Minutes.map_type_to_file(t) for t in force_list(type)]
        files = os.listdir(minutes_location)
        minutes = [
            Minutes(Minutes.map_file_to_type(f[:3]), parse_date(f[-14:-4], ' '), f[-3:])
            for f in files
            if not os.path.isdir(f) and f[:3] in type
        ]
        if year:
            minutes = [m for m in minutes if m.date.year in force_list(year)]
        return minutes

    @staticmethod
    def latest_minutes():
        minutes = Minutes.get_all_minutes()
        latest_date = max(m.date for m in minutes)
        latest = [m for m in minutes if m.date == latest_date][0]
        return latest

    @staticmethod
    def map_type_to_file(type):
        if type == MinutesType.Committee:
            return 'min'
        if type == MinutesType.AGM:
            return 'agm min'

    @staticmethod
    def map_file_to_type(file):
        if file == 'min':
            return MinutesType.Committee
        if file == 'agm min':
            return MinutesType.AGM




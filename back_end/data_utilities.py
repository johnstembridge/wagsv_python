import calendar
import datetime
import time
import math
import re
from decimal import Decimal

from globals.enumerations import EventType


# region dates
def decode_date(wdm, y):
    # wdm is in the form Friday 28 April, y is year
    if wdm:
        try:
            a = wdm.strip().split(' ')
            d = int(re.findall(r'\d+', a[1])[0])
            m = calendar.month_name[0:13].index(a[-1])
            return datetime.date(y, m, d)
        except:
            return datetime.date.today()
    else:
        return None


def encode_date(date):
    # result is in the form Friday 28 April
    if date is None:
        return ''
    return date.strftime('%A %d %B')


def encode_date_short(date):
    # result is in the form Fri 28 Apr
    if date is None:
        return ''
    return date.strftime('%a %d %b')


def decode_date_formal(wdm):
    # wdm is in the form 8th September 2013
    if wdm is not None:
        try:
            a = wdm.split(' ')
            d = int(re.findall(r'\d+', a[0])[0])
            m = calendar.month_name[0:13].index(a[1])
            y = int(a[2])
            return datetime.date(y, m, d)
        except:
            return datetime.date.today()
    else:
        return None


def encode_date_formal(date):
    # result is in the form 8th September 2013
    if date is None:
        return ''
    de = {1: 'st', 2: 'nd', 3: 'rd', 21: 'st', 22: 'nd', 23: 'rd', 31: 'st'}

    def custom_strftime(format, t):
        return time.strftime(format, t).replace('{TH}', str(t[2]) + de.get(t[2], 'th'))

    if isinstance(date, str):
        date = datetime.datetime.strptime(date, '%Y/%m/%d')

    return custom_strftime('{TH} %B %Y', date.timetuple())


def decode_date_range(dr, year):
    # dr is in the form Friday 22 - Sunday 24 April, y is year
    dr = dr.split('-')
    month = (dr[1].split(' '))[-1]
    dr[0] = dr[0] + ' ' + month
    return [decode_date(d, year) for d in dr]


def coerce_date(wdm, y, date):
    if not wdm: return date
    return decode_date(wdm, y)


def coerce_fmt_date(x):
    if type(x) == datetime.date:
        x = fmt_date(x)
    return x


def fmt_date(date):
    return date.strftime("%Y/%m/%d")


def parse_date(ymd):
    if type(ymd) is datetime.date:
        return ymd
    else:
        if len(ymd) > 0:
            date = ymd.split('/')
            return datetime.date(int(date[0]), int(date[1]), int(date[2]))
        else:
            return datetime.datetime.now().date()


def in_date_range(date, date_from, date_to):
    if date and date_from and date_to:
        return date_from <= date <= date_to
    else:
        return False


# endregion


def decode_price(amount):
    if not amount: amount = '0'
    if not is_num(amount): amount = '0'
    return Decimal(amount)


def encode_price(amount):
    if amount:
        return '{0:.2f}'.format(amount)
    else:
        return ''


def decode_time(time):
    if time and is_num(time):
        t = time.split('.')
        if len(t) < 2:
            t = t + ['0', '0']
        return datetime.time(int(t[0]), int(t[1]))
    else:
        return datetime.time()


def decode_event_type(event_type):
    if not event_type:
        return EventType.wags_vl_event
    return EventType(int(event_type))


def encode_event_type(event_type):
    return EventType[event_type].value


def sort_name_list(names):
    fl = [v.split(' ', 2) for v in names]
    fl.sort(key=lambda tup: (tup[1], tup[0]))
    return [n[0] + ' ' + n[1] for n in fl]


def normalise_name(name):
    return name.replace('+', ' ').title()


def lookup(item_list, items, index_origin=0):
    res = []
    for item in force_list(items):
        if item in item_list:
            i = index_origin + item_list.index(item)
        else:
            i = -1
        res.append(i)
    if type(items) is not list:
        res = res[0]
    return res


def force_list(x):
    if type(x) is tuple:
        x = list(x)
    if type(x) is not list:
        x = [x]
    return x


def force_lower(x):
    if type(x) is list:
        return [y.lower() for y in x]
    else:
        return x.lower()


def coerce(x, required_type):
    if x is not None and type(x) != required_type:
        x = required_type(x)
    return x


def fmt_num(num):
    return str(int(num) if num == math.floor(num) else num)


def first_or_default(list, default):
    if len(list) > 0:
        return list[0]
    else:
        return default


def is_num(s):
    return isinstance(s, str) and s.replace('.', '', 1).isdigit()


def to_float(s):
    if is_num(s):
        return float(s)
    else:
        return 0


def dequote(string):
    if string:
        if string.startswith('"') and string.endswith('"'):
            string = string[1:-1]
    return string


def enquote(string):
    return string if len(string) == 0 else '"' + string + '"'


def decode_address(address):
    if address and len(address) > 0:
        address = dequote(address)
        address = address.split(",")
        address = '\n'.join(address)
    return address


def encode_address(address):
    if not address: address = ''
    address = address.replace('\r', '')
    address = address.split('\n')
    address = ",".join(address)
    return enquote(address)


def encode_member_address(member: dict):
    return ', '.join(
        {k: member[k] for k in ['address1', 'address2', 'address3', 'address4'] if
         k in member and member[k].strip() != ''}.values())


def decode_member_address(address, member: dict):
    lines = address.split(',')
    for i in range(0, 4):
        if i < len(lines):
            line = lines[i].strip()
        else:
            line = ''
        member['address' + str(i + 1)] = line
    return member


def decode_directions(dir):
    if dir and len(dir) > 0:
        dir = dequote(dir)
        dir = dir.replace('\a', '\r\n')
    return dir


def encode_directions(dir):
    if not dir: dir = ''
    dir = dir.replace('\r\n', '\a')
    return enquote(dir)


def de_the(string):
    if string:
        if string.startswith('The '):
            string = string[4:]
    return string


def my_round(float_num):
    return math.floor(float_num + 0.5)
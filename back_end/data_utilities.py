import datetime
import calendar
import re
from decimal import Decimal
from enumerations import EventType

import math


def decode_date(wdm, y):
    # wdm is in the form Friday 28 April, y is year
    if wdm:
        try:
            a = wdm.split(' ')
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


def coerce_date(wdm, y, date):
    if not wdm: return date
    return decode_date(wdm, y)


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
        event_type = EventType.wags_vl_event.value
    return EventType(int(event_type)).name


def encode_event_type(event_type):
    return EventType[event_type].value


def sort_name_list(names):
    fl = [v.split(' ') for v in names]
    fl.sort(key=lambda tup: (tup[1], tup[0]))
    return [n[0] + ' ' + n[1] for n in fl]


def normalise_name(name):
    return name.title()


def lookup(item_list, items):
    res = []
    for item in force_list(items):
        if item in item_list:
            i = item_list.index(item)
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


def coerce(x, type):
    if type(x) != type:
        x = type(x)
    return x


def fmt_num(num):
    return str(int(num) if num == math.floor(num) else num)


def first_or_default(list, default):
    if len(list) > 0:
        return list[0]
    else:
        return default


def fmt_date(date):
    return date.strftime("%Y/%m/%d")


def is_num(s):
    return s.replace('.', '', 1).isdigit()


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
    address = address.replace('\r', '')
    address = address.split('\n')
    address = ",".join(address)
    return enquote(address)


def decode_directions(dir):
    if dir and len(dir) > 0:
        dir = dequote(dir)
        dir = dir.replace('\a', '\r\n')
    return dir


def encode_directions(dir):
    dir = dir.replace('\r\n', '\a')
    return enquote(dir)


def de_the(string):
    if string:
        if string.startswith('The '):
            string = string[4:]
    return string

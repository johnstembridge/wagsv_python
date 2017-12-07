import datetime
import calendar
import re
from decimal import Decimal
from enumerations import EventType

import math


def decode_date(wdm, y):
    # wdm is in the form Friday 28 April, y is year
    try:
        a = wdm.split(' ')
        d = int(re.findall(r'\d+', a[1])[0])
        m = calendar.month_name[0:13].index(a[-1])
        return datetime.date(y, m, d)
    except:
        return datetime.date(2017, 1, 1)


def encode_date(date):
    # result is in the form Friday 28 April
    return date.strftime('%A %d %B')


def coerce_date(wdm, y, date):
    if not wdm: return date
    return decode_date(wdm, y)


def decode_price(amount):
    if not amount: amount = '0'
    return Decimal(amount)


def encode_price(amount):
    return '{0:.2f}'.format(amount)


def decode_time(time):
    if time:
        t = time.split('.')
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


import os
from tempfile import mkstemp
from shutil import move
from collections import OrderedDict
from data_utilities import force_list, lookup
from operator import itemgetter


def get_record(file, key, value):
    delimiter = file_delimiter(file)
    keys = None
    with open(file, 'r') as f:
        for line in f:
            values = line.rstrip('\n').split(delimiter)
            if keys is None:
                keys = [k.lower() for k in values]
            else:
                rec = dict(zip(keys, values))
                if rec[key] == value:
                    return rec
    return dict(zip(keys, [None] * len(keys)))


def get_records(file, key, value):
    delimiter = file_delimiter(file)
    keys = None
    res = []
    with open(file, 'r') as f:
        for line in f:
            values = line.rstrip('\n').split(delimiter)
            if keys is None:
                keys = [k.lower() for k in values]
            else:
                rec = dict(zip(keys, values))
                if type(value) is list:
                    if rec[key] in value:
                        res.append(values)
                else:
                    if rec[key] == value:
                        res.append(values)
    return keys, res


def get_file(file):
    delimiter = file_delimiter(file)
    keys = None
    res = []
    with open(file, 'r') as f:
        for line in f:
            values = line.rstrip('\n').split(delimiter)
            if keys is None:
                keys = [k.lower() for k in values]
            else:
                res.append(values)
    return keys, res


def update_record(file, key, value, new_values):
    delimiter = file_delimiter(file)
    keys = None
    ft, target_file_path = mkstemp()
    os.close(ft)
    rec_updated = False
    with open(target_file_path, 'w') as target_file:
        with open(file, 'r') as source_file:
            for line in source_file:
                values = line.rstrip('\n').split(delimiter)
                if keys is None:
                    keys = [k.lower() for k in values]
                    new_line = line
                else:
                    rec = OrderedDict(zip(keys, values))
                    if rec[key] == value:
                        new_line = insert_rec_values(rec, new_values, delimiter)
                        rec_updated = True
                    else:
                        new_line = line
                target_file.write(new_line)
        if not rec_updated:  # add new record
            rec = OrderedDict(zip(keys, [''] * len(keys)))
            rec[key] = value
            new_line = insert_rec_values(rec, new_values, delimiter, True)
            target_file.write(new_line)
    os.remove(file)
    move(target_file_path, file)


def update_records(file, key, value, header, new_values):
    delimiter = file_delimiter(file)
    keys = None
    ft, target_file_path = mkstemp()
    os.close(ft)
    with open(target_file_path, 'w') as target_file:
        with open(file, 'r') as source_file:
            for line in source_file:
                values = line.rstrip('\n').split(delimiter)
                if keys is None:
                    keys = [k.lower() for k in values]
                    new_line = line
                else:
                    rec = OrderedDict(zip(keys, values))
                    v = add_keys(key, value, rec)
                    new_line = line
                    if keys_match(rec, key, v):
                        this_value = extract_new_record(header, new_values, dict(zip(key, v)))
                        if this_value:
                            new_line = insert_rec_values(rec, dict(zip(header, this_value)), delimiter)
                target_file.write(new_line)
        for values in new_values:  # add new records
            rec = OrderedDict(zip(keys, [''] * len(keys)))
            rec.update(dict(zip(key, value)))
            new_line = insert_rec_values(rec, dict(zip(header, values)), delimiter, True)
            target_file.write(new_line)
    os.remove(file)
    move(target_file_path, file)


def insert_rec_values(rec, new_values, delimiter, last_line=False):
    for item in new_values.keys():
        k = item
        if k in rec:
            rec[k] = new_values[item].replace(delimiter, ' ')
    res = (delimiter.join(rec.values()))
    if last_line:
        res = '\n' + res
    else:
        res = res + '\n'
    return res


def get_field(file, field):
    delimiter = file_delimiter(file)
    keys = None
    res = []
    with open(file, 'r') as f:
        for line in f:
            values = line.rstrip('\n').split(delimiter)
            if keys is None:
                keys = [k.lower() for k in values]
                if field not in keys:
                    raise ValueError('Field not found: ' + field)
            else:
                rec = dict(zip(keys, values))
                res.append(rec[field])
    if '' in res:
        res.remove('')
    return res


def file_delimiter(filename):
    file_type = (filename.split('.'))[1]
    delimiter = ',' if file_type == 'csv' else ':'
    return delimiter


def keys_match(rec, keys, values):
    keys = force_list(keys)
    values = force_list(values)
    rec_values = list(itemgetter(*keys)(rec))
    return rec_values == values


def add_keys(keys, values, rec):
    keys = force_list(keys)
    res = list(force_list(values))
    count = len(res)
    while count < len(keys):
        key = keys[count]
        if key in rec:
            res.append(rec[key])
        else:
            res.append(None)
        count += 1
    return res


def extract_new_record(header, new_values, kv):
    key_index = lookup(header, list(kv.keys()))
    extracted = None
    for values in new_values:
        match = True
        count = 0
        for k in key_index:
            if k != -1:
                match = match and values[k] == kv[header[k]]
            count += 1
        if match:
            extracted = list(values)
            new_values.remove(values)
            break
    return extracted





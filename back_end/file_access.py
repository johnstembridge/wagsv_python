import os
from tempfile import mkstemp
from shutil import move
from collections import OrderedDict
from data_utilities import force_list, lookup
from operator import itemgetter


def get_record(file, key, value):
    delimiter = file_delimiter(file)
    keys = None
    with my_open(file, 'r') as f:
        for line in f:
            values = line.rstrip('\n').split(delimiter)
            if keys is None:
                keys = [k.lower() for k in values]
            else:
                rec = dict(zip(keys, values))
                if type(value) is list and type(key) is not list:
                    if rec[key] in value:
                        return rec
                else:
                    if keys_match(rec, key, value):
                        return rec
                # rec = dict(zip(keys, values))
                # if rec[key] == value:
                #     return rec
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
                if type(value) is list and type(key) is not list:
                    if rec[key] in value:
                        res.append(values)
                else:
                    if keys_match(rec, key, value):
                        res.append(values)
    return keys, res


def get_file(file):
    delimiter = file_delimiter(file)
    keys = None
    res = []
    with my_open(file, 'r') as f:
        for line in f:
            values = line.rstrip('\n').split(delimiter)
            if keys is None:
                keys = [k.lower() for k in values]
            else:
                res.append(values)
    return keys, res


def update_record(file, key, new_rec):
    delimiter = file_delimiter(file)
    keys = None
    ft, target_file_path = mkstemp()
    os.close(ft)
    rec_updated = False
    with my_open(target_file_path, 'w') as target_file:
        with my_open(file, 'r') as source_file:
            for line in source_file:
                values = line.rstrip('\n').split(delimiter)
                if keys is None:
                    keys = [k.lower() for k in values]
                    new_line = line
                else:
                    rec = OrderedDict(zip(keys, values))
                    if type(new_rec) is not dict:
                        new_rec = dict(zip(keys, new_rec))
                    if keys_match(rec, key, new_rec):
                        new_line = insert_rec_values(rec, new_rec, delimiter)
                        rec_updated = True
                    else:
                        new_line = line
                target_file.write(new_line)
        if not rec_updated:  # add new record
            rec = OrderedDict(zip(keys, [''] * len(keys)))
            new_line = insert_rec_values(rec, new_rec, delimiter, True)
            target_file.write(new_line)
    os.remove(file)
    move(target_file_path, file)


def update_records(file, key, key_value, header, new_values):
    if len(new_values) == 0: return
    delimiter = file_delimiter(file)
    keys = None
    ft, target_file_path = mkstemp()
    os.close(ft)
    found = [False] * len(new_values)
    key = force_list(key)
    key_value = force_list(key_value)
    rec_key = (dict(zip(key[: len(key_value)], key_value)))
    with my_open(target_file_path, 'w') as target_file:
        with my_open(file, 'r') as source_file:
            for line in source_file:
                values = line.rstrip('\n').split(delimiter)
                if keys is None:
                    keys = [k.lower() for k in values]
                    new_line = line
                else:
                    rec = dict(zip(keys, values))
                    new_line = line
                    if keys_match(rec, list(rec_key), rec_key):
                        update_rec = get_matching_update_rec(rec, key, key_value, header, new_values, found)
                        if update_rec:
                            new_line = insert_rec_values(rec, update_rec, delimiter)
                target_file.write(new_line)
            # add new records
            for i in range(len(new_values)):
                if not found[i]:
                    values = new_values[i]
                    rec = OrderedDict(zip(keys, [''] * len(keys)))
                    rec.update(dict(zip(key, key_value)))
                    new_line = insert_rec_values(rec, dict(zip(header, values)), delimiter, True)
                    target_file.write(new_line)
    os.remove(file)
    move(target_file_path, file)


def get_matching_update_rec(rec, key, key_value, header, new_values, found):
    for i in range(len(new_values)):
        new = new_values[i]
        new_dict = dict(zip(header, new))
        add_keys(key, key_value, new_dict)
        if keys_match(rec, key, new_dict):
            found[i] = True
            return new_dict
    return None


def insert_rec_values(rec, new_values, delimiter, last_line=False):
    for item in new_values.keys():
        k = item
        if k in rec:
            rec[k] = str(new_values[item]).replace(delimiter, ' ')
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
    with my_open(file, 'r') as f:
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


def get_fields(file, fields):
    delimiter = file_delimiter(file)
    keys = None
    res = []
    with my_open(file, 'r') as f:
        for line in f:
            values = line.rstrip('\n').split(delimiter)
            if keys is None:
                keys = [k.lower() for k in values]
                for field in fields:
                    if field not in keys:
                        raise ValueError('Field not found: ' + field)
                if len(fields) == 0: fields = keys
            else:
                rec = dict(zip(keys, values))
                v = {field: rec[field] for field in fields}
                res.append(v)
    if '' in res:
        res.remove('')
    return res


def file_delimiter(filename):
    file_type = (filename.split('.'))[1]
    if file_type == 'csv': delimiter = ','
    elif file_type == 'tab': delimiter = ':'
    elif file_type == 'txt': delimiter = '\t'
    else: delimiter = ' '
    return delimiter


def keys_match(rec, keys, new_rec):
    try:
        keys = force_list(keys)
        if type(new_rec) is dict:
            new_values = force_list(itemgetter(*keys)(new_rec))
        else:
            new_values = force_list(new_rec)
        rec_values = force_list(itemgetter(*keys)(rec))
        return rec_values == new_values
    except Exception as inst:
        return None


def add_keys(keys, key_values, new_data):
    keys = force_list(keys)
    for i in range(len(keys)):
        if keys[i] not in new_data:
            new_data[keys[i]] = key_values[i]


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


def my_open(filename, mode):
    return open(filename, mode, encoding="latin-1")





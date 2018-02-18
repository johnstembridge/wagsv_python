import os
import json
from flask import url_for as flask_url_for


old_site = 'http://80.82.113.181/'


def read():
    file_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(file_path) as json_data_file:
        de_commented = ''.join(line for line in json_data_file if not line.strip().startswith('//'))
        cfg = json.loads(de_commented)
    return cfg


def get(key):
    return read()[key]


def url_for_admin(endpoint, **values):
    return url_for('admin', endpoint, **values)


def url_for_user(endpoint, **values):
    return url_for('user', endpoint, **values)


def url_for_old_site(end):
    end = end.replace(" ", "%20")
    return get('locations')['base_url'] + end


def url_for_old_service(end):
    prefix = get('locations')['base_url'] + '/cgi-bin/members/'
    return prefix + end


def url_for(app, endpoint, **values):
    url = flask_url_for(endpoint, **values)
    prefix = get('url_prefix')[app]
    if prefix:
        url = prefix + url
    return url

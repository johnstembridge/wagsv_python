import os
import json
from flask import url_for as flask_url_for


def read():
    file_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(file_path) as json_data_file:
        de_commented = ''.join(line for line in json_data_file if not line.strip().startswith('//'))
        cfg = json.loads(de_commented)
    return cfg


def get(key):
    return read()[key]


def url_for_admin(endpoint, **values):
    return url_for_app('admin', endpoint, **values)


def url_for_user(endpoint, **values):
    return url_for_app('user', endpoint, **values)


def url_for_app(app, endpoint, **values):
    url = flask_url_for(endpoint, **values)
    prefix = get('url_prefix')[app]
    if prefix:
        url = prefix + url
    return url


def url_for_wags_site(end):
    end = end.replace(" ", "%20")
    return get('locations')['base_url'] + end


def url_for_html(*paths):
    return os.path.join(get('locations')['base_url'], *paths)


def path_for_app(app, path):
    prefix = get('url_prefix')[app]
    url = os.path.join(prefix, path)
    return url


def full_url_for_app(app, url):
    prefix = get('url_prefix')[app]
    url = os.path.join(get('locations')['base_url'], prefix, url)
    return url

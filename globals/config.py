import os
import json
from flask import url_for as flask_url_for
from werkzeug.urls import url_parse, url_unparse


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
    url = flask_url_for(endpoint, _scheme='https', _external=True, **values)
    url_ = url_parse(url)
    new = url_unparse(
        ('https',
         url_.netloc,
         path_for_app(app, url_.path),
         url_.query,
         url_.fragment
         )
    )
    return new


def url_for_wags_site(end):
    end = end.replace(" ", "%20")
    return get('locations')['base_url'] + end


def url_for_html(*paths):
    return os.path.join(get('locations')['base_url'], *paths)


def path_for_app(app, path):
    prefix = get('url_prefix')[app].replace('/', '')
    url = (prefix + '/' + path).replace('//', '/')
    return url


def full_url_for_app(app, url):
    prefix = get('url_prefix')[app]
    url = os.path.join(get('locations')['base_url'], prefix, url)
    return url


def adjust_url_for_https(app, url=None):
    if url:
        url_ = url_parse(url)
        new = url_unparse(
            ('https',
             url_.netloc,
             path_for_app(app, url_.path),
             url_.query,
             url_.fragment
             )
        )
    else:
        new = full_url_for_app(app, 'index')
    return new

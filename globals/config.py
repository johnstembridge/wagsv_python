import os
import json


def read():
    file_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(file_path) as json_data_file:
        # cfg = json.load(json_data_file)
        de_commented = ''.join(line for line in json_data_file if not line.startswith('//'))
        cfg = json.loads(de_commented)
    return cfg


def get(key):
    return read()[key]

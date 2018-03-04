from operator import itemgetter
import itertools

from .data_utilities import lookup, force_list


class Table:
    def __init__(self, head, data):
        self.head = head
        self.data = data

    def get_column(self, col_name):
        index = lookup(self.head, col_name)
        return [v[index] for v in self.data]

    def sort(self, col_names, reverse=False):
        index = lookup(self.head, force_list(col_names))
        self.data.sort(key=itemgetter(*index), reverse=reverse)

    def groupby(self, col_names):
        index = lookup(self.head, force_list(col_names))
        return itertools.groupby(self.data, itemgetter(*index))

    def add_column(self, col_name, col):
        self.data = [list(itertools.chain(d, [c])) for d, c in zip(self.data, col)]
        self.head.append(col_name)

    def column_index(self, col_names):
        return lookup(self.head, col_names)
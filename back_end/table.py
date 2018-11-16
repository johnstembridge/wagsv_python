from operator import itemgetter
import itertools

from .data_utilities import lookup, force_list, coerce


class Table:
    def __init__(self, head, data):
        self.head = head
        self.data = data

    def get_columns(self, col_names):
        index = self.column_index(col_names)
        if type(col_names) is list:
            return [itemgetter(*index)(r) for r in self.data]
        else:
            return [v[index] for v in self.data]

    def sort(self, col_names, reverse=False):
        index = self.column_index(force_list(col_names))
        self.data.sort(key=itemgetter(*index), reverse=reverse)

    def sort_using(self, values, reverse=False):
        self.data = [x for _, x in sorted(zip(values, self.data), reverse=reverse)]

    def top_n(self, n):
        # assume sorted
        self.data = self.data[:min(n, len(self.data))]

    def group_by(self, col_names):
        index = self.column_index(force_list(col_names))
        return itertools.groupby(self.data, itemgetter(*index))

    def add_column(self, col_name, col):
        self.data = [list(itertools.chain(d, [c])) for d, c in zip(self.data, col)]
        self.head.append(col_name)

    def rename_column(self, old, new):
        self.head[self.column_index(old)] = new

    def coerce_column(self, col, type):
        i = self.column_index(col)
        for row in self.data:
            row[i] = coerce(row[i], type)

    def coerce_column_using(self, col, fn):
        i = self.column_index(col)
        for row in self.data:
            row[i] = fn(row[i])

    def coerce_columns(self, cols, type):
        for col in cols:
            self.coerce_column(col, type)

    def where(self, lu_fn):
        return Table(self.head, [d for d in self.data if lu_fn(dict(zip(self.head, d)))])

    def column_index(self, col_names):
        return lookup(self.head, col_names)

    def select_columns(self, col_names):
        index = self.column_index(col_names)
        head = itemgetter(*index)(self.head)
        return Table(head, [itemgetter(*index)(r) for r in self.data])

    def select_rows(self, sel_fn):
        return Table(self.head, [d for d in self.data if sel_fn(dict(zip(self.head, d)))])

    def update_row(self, key, value, new_data):
        keys = self.get_columns(key)
        if value in keys:
            index = keys.index(value)
            self.data[index] = new_data
        else:
            self.data.append(new_data)

    def update_column(self, col_name, col):
        index = self.column_index(col_name)

        def update_value(row, index, value):
            row[index] = value
            return row
        self.data = [update_value(list(d), index, c) for d, c in zip(self.data, col)]

    def rows(self):
        for row in self.data:
            yield dict(zip(self.head, row))

    def __str__(self):
        res = ['\t'.join([str(item) for item in row]) for row in [self.head] + self.data]
        return '\n'.join(res)

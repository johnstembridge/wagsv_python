def set_select_field(field, item_name, choices, default_selection):
    if len(choices) > 0 and isinstance(choices[0], tuple):
            items = choices
    else:
        items = [(c, c) for c in choices]
    field.choices = [('', 'Choose {} ...'.format(item_name))] + items
    default = [c[0] for c in items if c[0] == default_selection]
    if len(default) > 0:
        field.data = field.default = default[0]
    pass


def set_select_field_from_enum(field, item_name, choices, default_selection):
    items = [(s.value, s.name) for s in choices]
    default_selection = default_selection.value
    set_select_field(field, item_name, items, default_selection)

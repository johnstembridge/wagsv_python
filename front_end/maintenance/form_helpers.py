
def set_select_field(field, item_name, choices, default_selection):
    if len(choices) > 0 and isinstance(choices[0], tuple):
        items = choices
    else:
        items = [(c, c) for c in choices]
    field.choices = [('', 'Choose {} ...'.format(item_name))] + items
    default = [c for c in choices if c == default_selection]
    if len(default) > 0:
        field.data = default[0]

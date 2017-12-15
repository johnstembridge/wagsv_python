
def set_select_field(field, item_name, choices, default_selection):
    field.choices = [('', 'Choose {} ...'.format(item_name))] + [(c, c) for c in choices]
    default = [c for c in choices if c == default_selection]
    if len(default) > 0:
        field.data = default[0]

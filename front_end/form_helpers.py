from flask import flash

from back_end.data_utilities import coerce


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')


def set_select_field(field, item_name, choices, default_selection=None):
    if len(choices) > 0 and isinstance(choices[0], tuple):
            items = choices
    else:
        items = [(c, c) for c in choices]
    field.choices = [(None, 'Choose {} ...'.format(item_name))] + items
    if default_selection:
        default = [c[0] for c in items if c[0] == default_selection]
        if len(default) > 0:
            field.data = field.default = default[0]


def set_select_field_from_enum(field, enum_obj, default_selection=None):
    field.choices = enum_obj.choices()
    if default_selection:
        if type(default_selection) != enum_obj:
            default_selection = enum_obj(coerce(default_selection, int))
        field.default = default_selection
    field.coerce = enum_obj.coerce

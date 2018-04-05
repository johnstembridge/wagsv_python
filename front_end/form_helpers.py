from flask import flash, url_for

from back_end.data_utilities import coerce, force_list
from globals import config


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


def render_link(url, text="", image=None):
    if image:
        return '<a href="{}"><img title="{}" src="{}"></a>'.format(url, text, image)
    if text:
        return '<a href="{}">{}</a>'.format(url, text)


def render_html(template, **kwargs):
    import jinja2
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath='../templates/'))
    template = env.get_template(template)
    return template.render(url_for=url_for, **kwargs)


def update_html(html, pairs):
    for id, value in pairs.items():
        i = html.find(id)
        start = i + 1 + html[i:].find('>')
        length = html[start:].find('<')
        html = html[:start] + value + html[start + length:]
    return html


def get_elements_from_html(html, ids):
    result = {}
    for id in force_list(ids):
        i = html.find(id)
        if i >= 0:
            start = i + 1 + html[i:].find('>')
            length = html[start:].find('<')
            result[id] = html[start: start + length]
    return result

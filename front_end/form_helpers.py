from flask import flash, url_for, current_app
import os

from back_end.data_utilities import force_list


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
    if item_name:
        field.choices = [(0, 'Choose {} ...'.format(item_name))] + items
    else:
        field.choices = items
    if default_selection:
        default = [c for c in items if c[1] == default_selection]
        if len(default) > 0:
            field.data = default[0][0]


def render_link(url, text="", image=None, icon=None, target=None):
    target = ' target="{}"'.format(target) if target else ''
    if image:
        return '<a href="{}"{}><img title="{}" src="{}"></a>'.format(url, target, text, image)
    if icon:
        if icon == 'fa-link':
            icon = '<i class="fa fa-chevron-circle-right" style="font-size:20px;color:#6E1285"></i>'
        return '<a href="{}"{} title="{}" class="icon-block">{}'.format(url, target, text, icon)
    if text:
        return '<a href="{}"{}>{}</a>'.format(url, target, text)


def render_html(template, **kwargs):
    import jinja2
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath='templates/'))
    template = env.get_template(template)
    return template.render(url_for=url_for, **kwargs)


def template_exists(template):
    return os.path.exists(os.path.join(current_app.jinja_loader.searchpath[0], template))


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

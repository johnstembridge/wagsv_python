from flask import flash, url_for, current_app, request
from wtforms import SelectField
import os

from back_end.data_utilities import force_list
from globals import config


class MySelectField(SelectField):

    def pre_validate(self, form):
        if self.flags.required and self.data == 0:
            raise ValueError(self.gettext('Please choose an option'))


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')


def set_select_field(field, choices, item_name=None, default_selection=None):
    if len(choices) > 0 and isinstance(choices[0], tuple):
        items = choices
    else:
        items = [(c, c) for c in choices]
    if item_name:
        field.choices = [(0, 'Choose {} ...'.format(item_name))] + items
    else:
        field.choices = items
    if default_selection:
        field.default = default_selection
        field.data = default_selection


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
    return update_html(template, kwargs)


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


def line_break(text, line_break_characters=None):
    br = '<br/>'
    if type(text) is list:
        res = br.join([t for t in text if len(t) > 0])
    else:
        line_break_characters = force_list(line_break_characters)
        for r in line_break_characters[1:]:
            text = text.replace(r, line_break_characters[0])
        res = line_break(text.split(line_break_characters[0]))
    return res


def browser_info():
    browser = request.user_agent.browser  # msie/firefox/safari/opera
    version = request.user_agent.version and int(request.user_agent.version.split('.')[0])
    platform = request.user_agent.platform  # android/iphone/macos/windows
    uas = request.user_agent.string
    return {'browser': browser,
            'version': version,
            'platform': platform,
            'user_agent': uas}

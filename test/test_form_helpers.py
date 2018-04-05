import unittest
import front_end.form_helpers as fh
from back_end.file_access import get_file_contents


class TestFormHelpers(unittest.TestCase):
    def test_render_html(self):
        template = 'static/event_report.html'
        html = fh.render_html(template,
                              title='Wimbledon Common 2018/03/29',
                              winner='Dave Middleton',
                              ld='Andy Burn',
                              ntp='Anthony Shutes',
                              month_year='March 2018'
                              )
        pass

    def test_update_html(self):
        html = '''
<html>
<head>
    <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='styles/wags.css') }}">
    <Title>{{ title }}</title>
</head>
<body>
<h2>{{ title }}</h2>

<table>
    <tr>
        <td class="head"><b>Winner:</b></td>
        <td id="winner">{{ winner }}</td>
    <tr>
        <td class="head"><b>Nearest the Pin:</b></td>
        <td id="ntp">{{ ntp }}</td>
    <tr>
        <td class="head"><b>Longest Drive:</b></td>
        <td id="ld">{{ ld }}</td>
</table>
<p id="report">{{ report }}</p>
<p id="month_year">&#169; Wimbledon Ancient Golf Society<br> {{ month_year }}</p>
</body>
</html>'''
        subs = {'winner': 'Joe Blow', 'ld': 'Fred', 'ntp': 'Jim',
                  'report': 'Whilst the morning round saw sunshine, it was wet and windy for the main event'}
        html = fh.update_html(html, subs)

        v = fh.get_elements_from_html(html, list(subs.keys()))
        pass


if __name__ == '__main__':
    unittest.main()

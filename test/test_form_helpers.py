import unittest
import front_end.form_helpers as fh


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


if __name__ == '__main__':
    unittest.main()

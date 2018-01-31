from back_end.interface import get_all_news
from back_end.data_utilities import decode_date_formal, fmt_date, encode_date_formal


class News:
    def __init__(self):
        self.all = get_all_news()
        self.head = self.all[0]
        self.dates = self._index(self.all[1:])
        self.news = self.all[1:]

    @staticmethod
    def _index(all):
        inx = [section[1] for section in all]
        dates = [fmt_date(decode_date_formal(h.strip()[6:-4])) for h in inx]
        return dates

    def get_new_item_for(self, date):
        return NewsItem.from_html(self.news[self.dates.index(date)])


class NewsItem:
    date = None
    lines = []

    @staticmethod
    def from_html(html_lines):
        # Creates a news item from html in the format:
        # <hr/>
        # <p><b>8th September 2013</b>
        # <ul>
        # <li>Line</li>
        # <li><a href="../2013/fixtures.htm" title="book now">Booking now open for Wimbledon Common Wednesday 25th September</a></li>
        # <li><a href="../minutes/min 2013 09 04.htm">Minutes of email committee meeting held on 4th September</a> from Anthony Shutes</li>
        # </ul>
        item = NewsItem()
        item.date = fmt_date(decode_date_formal(html_lines[1][6:-5]))
        item.lines = []
        for html_line in html_lines[3: -1]:
            line = html_line.strip()[4: -5]
            item.lines.append(line)
        return item

    def to_html(self):
        html = []
        html.append('<hr/>')
        html.append('<p><b>{}</b>'.format(encode_date_formal(self.date)))
        html.append('<ul>')
        for line in self.lines:
            html.append('<li>{}</li>'.format(line))
        html.append('<ul/>')
        return '\n'.join(html)

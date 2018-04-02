from datetime import datetime

from back_end.data_utilities import decode_date_formal, fmt_date, encode_date_formal, coerce_fmt_date, dequote
from back_end.interface import news_file, front_page_header_file
from file_access import my_open, update_html_element, write_file


class News:
    def __init__(self):
        all = News.get_all_news()
        self.head = all[0]
        self.dates = self._index(all[1:])
        self.news = all[1:]

    def get_news_day(self, date):
        return NewsDay.from_html(self.news[self.dates.index(date)])

    def add_news_day(self, newsday):
        html = newsday.to_html()
        self.dates = newsday.date + self.dates
        self.news = [html] + self.news

    def update_news_day(self, newsday):
        date = newsday.date
        html = newsday.to_html()
        i = self.dates.index(date)
        self.news[i] = html

    def news_select_choices(self):
        id = [d.replace('/', '-') for d in self.dates]
        return list(zip(id, self.dates))

    def publish(self, news_day):
        if news_day.date in self.dates:
            orig = self.get_news_day(news_day.date)
            orig.merge(news_day)
            news_day = orig
            self.update_news_day(news_day)
        else:
            self.add_news_day(news_day)
        self.write_all_news()
        News.update_front_page(news_day.date)
        pass

    def write_all_news(self):
        write_file(news_file(), ''.join([self.head] + self.news))

    @staticmethod
    def update_front_page(date):
        update_html_element(front_page_header_file(), 'last_updated', date)

    @staticmethod
    def get_all_news():
        with my_open(news_file(), 'r') as fh:
            res = []
            section = []
            for line in fh:
                if line.startswith('<hr'):
                    if len(section) != 0:
                        res.append(''.join(section))
                    section = [line]
                else:
                    section.append(line)
        res.append(''.join(section))
        return res

    @staticmethod
    def _index(all):
        inx = [section.split('\n')[1] for section in all]
        dates = [fmt_date(decode_date_formal(h.strip()[6:-4])) for h in inx]
        return dates


class NewsDay:
    def __init__(self, date=None, items=[]):
        self.date = coerce_fmt_date(date or datetime.today().date())
        if type(items) is not list:
            items = [items]
        self.items = items

    def merge(self, extra):
        self.items += extra.items

    @staticmethod
    def from_html(html):
        # Creates a news item from html in the format:
        # <hr/>
        # <p><b>8th September 2013</b>
        # <ul>
        # <li>Line</li>
        # <li><a href="../2013/fixtures.htm" title="book now">Booking now open for Wimbledon Common Wednesday 25th September</a></li>
        # <li><a href="../minutes/min 2013 09 04.htm">Minutes of email committee meeting held on 4th September</a> from Anthony Shutes</li>
        # </ul>
        html_lines = html.split('\n')
        day = NewsDay()
        day.date = fmt_date(decode_date_formal(html_lines[1][6:-4]))
        day.items = []
        for html_line in html_lines[3: -2]:
            html_line = html_line.rstrip()[4:-5]
            if html_line.startswith("<a href="):
                end = html_line.find('>')
                link = html_line[8:end].rstrip()
                text = html_line[end+1:-4]
                t = link.find('title=')
                if t >= 0:
                    title = link[t+6:].rstrip()
                    link = link[:t].rstrip()
                else:
                    title = None
                item = NewsItem(text.rstrip(), dequote(link), dequote(title))
            else:
                item = NewsItem(html_line)
            day.items.append(item)
        return day

    def to_html(self):
        html = [
            '<hr/>',
            '<p><b>{}</b>'.format(encode_date_formal(self.date)),
            '<ul>'
        ]
        for item in self.items:
            html.append(item.to_html())
        html.append('</ul>')
        return ('\n'.join(html)) + '\n'


class NewsItem:
    def __init__(self, text, link=None, title=None):
        self.text = text
        self.link = link
        self.title = title

    def to_html(self):
        html = '<li>'
        if self.link:
            html += '<a href="{}"'.format(self.link)
            if self.title:
                html += ' title="{}"'.format(self.title)
            html += '>{}</a>'.format(self.text)
        else:
            html += self.text
        html += '</li>'
        return html

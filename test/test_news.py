import unittest

from models.news import News, NewsDay, NewsItem


class TestNews(unittest.TestCase):
    def test_make_news(self):
        news = News()
        self.assertTrue(news is not None)
        date = '2018/03/11' # '2018/03/11'
        day = news.get_news_day(date)
        html = day.to_html()
        orig = news.news[news.dates.index(date)]
        self.assertEqual(html, orig)

    # def test_make_news(self):
    #     news = News()
    #     self.assertTrue(news is not None)
    #     for date in news.dates:
    #         day = news.get_news_day(date)
    #         html = day.to_html()
    #         orig = ''.join(news.news[news.dates.index(date)])
    #         if  html != orig[:-1]:
    #             pass
    #     pass

    # def test_publish_news(self):
    #     news = News()
    #     item = NewsItem(text='news item', link='link/to/referred/item')
    #     day = NewsDay(date='2018/03/11', items=[item])
    #     news.publish(day)


if __name__ == '__main__':
    unittest.main()

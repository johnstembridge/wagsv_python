import unittest

from models.news import News


class TestNews(unittest.TestCase):
    def test_make_news(self):
        news = News()
        self.assertTrue(news is not None)
        x = news.get_new_item_for('2013/08/05')
        h = x.to_html()
        pass


if __name__ == '__main__':
    unittest.main()

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, SelectField, FieldList, FormField, DateField
from back_end.data_utilities import parse_date
from front_end.form_helpers import set_select_field
from models.news import News, NewsDay, NewsItem
from datetime import datetime


class NewsListForm(FlaskForm):
    news_item = SelectField(label='News Item')
    edit_news = SubmitField(label='Edit news item')
    add_news = SubmitField(label='Add news item')

    def populate_news_list(self):
        news = News()
        set_select_field(self.news_item, 'news item', news.news_select_choices(), '')


class NewsItemForm(FlaskForm):
    text = StringField(label='Text')
    link = StringField(label='url')
    title = StringField(label='Title')


class NewsDayForm(FlaskForm):
    items = FieldList(FormField(NewsItemForm))
    date = DateField(label='date')
    orig_date = HiddenField()
    save = SubmitField(label='Save')

    def populate_news_day(self, news_date=None):
        if news_date is not None:
            news_date = news_date.replace('-', '/')
            news_day = News().get_news_day(news_date)
        else:
            news_day = NewsDay(date=datetime.date.today())

        self.date.data = parse_date(news_day.date)
        self.orig_date.data = parse_date(news_day.date)
        for i in range(5):
            if i < len(news_day.items):
                item = news_day.items[i]
            else:
                item = NewsItem()
            item_form = NewsItemForm()
            item_form.text = item.text
            item_form.link = item.link
            item_form.title = item.title
            self.items.append_entry(item_form)

    def save_news_day(self, news_date):
        date = self.date.data
        orig_date = self.orig_date.data
        items = []
        for item in self.items:
            if len(item.text.data) > 0:
                items.append((item.text.data, item.link.data, item.title.data))

        newsday = NewsDay(date, items)
        News().save_newsday(newsday)
        return True
